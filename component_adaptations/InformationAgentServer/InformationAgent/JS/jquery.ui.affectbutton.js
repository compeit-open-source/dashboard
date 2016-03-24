(function($, window, undefined) { // begin plugin

/*
 * TODO
 * - implement _setOption() to allow changing options during lifetime
 * - split separate area to click (expect trouble on mobile devices), this
 *   means splitting off the mouse event handlers and creating our own custom
 *   events.
 * - handle or remove inline TODOs
 * 
 * - document(!)
 * - make minified version
 * - give the whole shebang to Joost Broekens (TUDelft) for validation
 * 
 * TODO maybe
 * - use requestAnimationFrame() in stead of setTimeout()
 * - move core (non-widget stuff) into separate file, for use without jQuery/UI?
 * - allow styling from CSS somehow?
 * 
 */

// The following is at the heart of it all: survey-optimized weights, due to the
// work of Joost Broekens et. al.
// For each of 9 archetypes: radius of influence, affect (x3), features (x8)
var NUMFEATS = 8,
	NUMARCHS = 9,
	ARCHETYPES = [
	    1.7,       0,   0,   0,        0,   0,   0,   0,   0, -.5,   0,   1,
	    1.3,      -1,  -1,  -1,       -1,  -1,  -1,   1,  -1,  -1,  -1,   1,
	    1.3,      -1,  -1,   1,      -.3,   0,   0,  -1,  -1, -.5, -.5,   1,
	    1.3,      -1,   1,  -1,        1,   1, -.8,  .8,   0,   0, -.3,  .5,
	    1.3,      -1,   1,   1,       .5,   0,  .8, -.8,   1,   1,  -1,   1,
	    1.3,       1,  -1,  -1,       -1,  -1,   0,   0,   0,  -1,  .7,   1,
	    1.3,       1,  -1,   1,      -.5,   0,   0,   0,   0, -.5,   1,   1,
	    1.3,       1,   1,  -1,       .3,   1,   0,   0,-1.5,  .7,  .5, -.5,
	    1.3,       1,   1,   1,       .5,  .5,   0,   0,   1,  .5,   1,  .5
	];	

$.widget('ui.affectbutton', { // begin widget
	
	// ---- user-configurable options: ----
	// defaults correspond to Joost Broekens original version
	options: {
		
		//behavior
		active:				true,
		touch:				true,
		offset:				0, // index of initial affect (archetype 0,...,8)
		interval:			40, // (maximum) 25 frames per second
		
		// choose _setXY version 1 or 2
		mapper:				'2',
		// for both _setXY versions:
		sensitivity:		1.1,
		// for _setXY1:
		factor:				0.55,
		// for _setXY2:
		sigmoidSteepness:	11,
		sigmoidZero:		8.5,
		swapAD:				false,
		
		// appearance
		cursor:				'crosshair',
		lineCap:			'round',
		scaleMin:			10,
		scaleMax:			370, // ? if it helps but 360 is very composite
		padding:			2,
		
		ground: {
			fill0:			'#edfeff',
			fill1:			'#cbdcff',
			stroke:			'#45609c',
			width:			1
		},
		
		face: {
			fill0:			'#ffc800',
			fill1:			'',
			stroke:			'#f0c030',
			width:			1,
			shadow:			'#301020',
			shadowX:		0,
			shadowY:		0
		},
		
		brow: {
			stroke:			'#000000',
			width:			3,
			shadow:			'#c0a060',
			shadowX:		0,
			shadowY:		0
		},
		
		eye: {
			fill0:			'#ffffff',
			stroke:			'#ffffff',
			width:			.1
		},
		
		iris: {
			fill0:			'#00c8c8',
			fill1:			'',
			stroke:			'#00c8c8',
			width:			.5
		},
		
		pupil: {
			fill0:			'#000000',
			stroke:			'#00ffff',
			width:			.25
		},
		
		mouth: {
			fill0:			'#ffc800',
			fill1:			'',
			stroke:			'#c86400',
			width:			1
		},
		
		teeth: {
			fill0:			'#ffffff',
			shadow:			'',
			stroke:			'#ffc800',
			width:			1,
			grid:			[.1, .25, .5, .75, .9]
		}
	},
	
	
	// ---- standard widget functions: ----
	
	_create: function() {
		// TODO assert that this.element is appropriate
		// TODO assert that (important) options have sane values
		var k = this.options.offset * (4 + NUMFEATS), m;
		
		$.extend(this, {
			state: {
				pleasure: ARCHETYPES[k + 1],
				arousal: ARCHETYPES[k + 2],
				dominance: ARCHETYPES[k + 3]
			},
			feats: ARCHETYPES.slice(k + 4, k + 4 + NUMFEATS),
			width: 0,
			height: 0,
			active: this.options.active,
			repaint: true,
			down: false
		});
		
		this.element.css('cursor', this.options.cursor);
		m = this._eventMap();
		$.each(m, function(k, v) { // TODO is there a less ugly way to do this?
			delete m[k];
			m[k + '.ui-affectbutton'] = v;
		});
		this.element.on(m);
	},
	
	_init: function() {
		if (this.active) {
			this.active = false;//forced change
			this.alive(true);
		} else {
			this.repaint = true;
			this._paint();
		}
	},
	
	destroy: function() {
		this.element.off('.ui-affectbutton');
	},
	
	
	// ---- public plugin functions: ----
	
	alive: function(a) {
		if (arguments.length == 0) {
			return this.active;
		}
		a = !!a;
		if (a != this.active) {
			this.active = a;
			if (a) {
				this.repaint = true;
				this._paint();
			} else {
				window.clearTimeout(this.timer);
			}
		}
	},
	
	affect: function(a, v) {
		var thiz = this;
		switch (arguments.length) {
			case 0:
				return $.extend({}, this.state);
			case 1:
				$.each(a, function(k, w) {
					thiz.affect(k, w);
				});
				break;
			case 2:
				if (thiz.state.hasOwnProperty(a) && !isNaN(v = parseFloat(v))) {
					thiz.state[a] = thiz._clip(v);
				}
				break;
			default:
				throw 'too many args'; 
		}
		this.repaint = true;
		if (!this.active) {
			this._paint();
		}
	},
	
	reset: function() {
		this.mouseX = this.mouseY = 0;
		this.affect({pleasure: 0, arousal: 0, dominance: 0});
	},
	
	
	// ---- private plugin functions: ----
	
	_eventMap: function() {
		var thiz = this;
		return {
			'selectstart': false,
			'mouseenter': function(e) {
				thiz.down = false;
				thiz.clicked=false;
				return false;
			},
			'mouseleave': function(e) {
				thiz.down = false;
				thiz.clicked=false;
				return false;
			},
			'mousedown': function(e) {
				thiz.down = true;
				thiz.clicked=false;
				thiz._doMouse(e);
				return false;
			},
			'mousemove': function(e) {
				thiz.clicked=false;
				//thiz._doMouse(e);
				return false;
			},
			'mouseup': function(e) {
				if (thiz.down) thiz.clicked=true;
				thiz.down = false;
				thiz._doMouse(e);
				return false;
			}
		};
	},
	
	_doMouse: function(e) {
		var off;
		if (this.active /*&& (this.down || !this.options.touch)*/) {
			off = this.element.offset();
			this.mouseX = e.pageX - off.left;
			this.mouseY = e.pageY - off.top;
			this['_setXY' + this.options.mapper](2 * this.mouseX/(this.width - 1) - 1
					, 1 - 2 * this.mouseY/(this.height - 1));
			if (this.clicked /*|| this.down*/) {
				this.element.trigger('affectchanged', [this.affect()]);
			}
		}
	},
	
	_setXY1: function(x, y) {
		var f = this.options.factor,
			s = this.options.sensitivity,
			p = s * this._clip(x),
			d = s * this._clip(y),
			a = 2 * ((Math.max(Math.abs(p), Math.abs(d), f) - f) / (1 - f)) - 1;
		this.affect({
			pleasure: p,
			arousal: a,
			dominance: d
		});
	},
	
	// Updated algorithm adapted from Joost's version of 17 July 2012
	// Note: options.factor no longer used in this version
	_setXY2: function(x, y) {
		var p = this.options.sensitivity * x,
			d = this.options.sensitivity * y,
			n = Math.max(Math.abs(p), Math.abs(d)),
			a = 2.1 / (1+Math.exp(-(this.options.sigmoidSteepness * n - this.options.sigmoidZero)))  - 1;
		this.affect({
			pleasure: p,
			arousal: this.options.swapAD ? d : a,
			dominance: this.options.swapAD ? a : d
		});
	},
	
	_updateFeatures: function() {
		var i, j, k, v, w, r, d1, d2, d3;
		for (i = 0; i < NUMFEATS; i++) {
			this.feats[i] = 0;
		}
		w = 0;
		for (j = 0; j < NUMARCHS; j++) {
			k = j * (4 + NUMFEATS);
			if ((r = ARCHETYPES[k++]) > 0
			&& (d1 = Math.abs(this.state.pleasure - ARCHETYPES[k++])) < r
			&& (d2 = Math.abs(this.state.arousal - ARCHETYPES[k++])) < r
			&& (d3 = Math.abs(this.state.dominance - ARCHETYPES[k++])) < r
			&& (v = Math.sqrt(d1*d1 + d2*d2 + d3*d3)) < r) {
				v = r - v;
				for (i = 0; i < NUMFEATS; i++) {
					this.feats[i] += v * ARCHETYPES[k++];
				}
				w += v;
			}
		}
		for (i = 0; i < NUMFEATS; i++) {
			this.feats[i] /= w;
		}
	},
	
	
	// TODO explain/rename variables(!)
	// TODO still waaaay too long, split up further
	_paint: function() {
		var t, c, w, h, u, s, g, bew, beh, bmw, bmh,
			cx, cy, gx, gy, fx, fy, ex, ey, ew, eh, mx, my, mu, ml, tv, ty, th;
		t = Date.now();
		
		if (!(w = this.element.width())
		|| !(h = this.element.height())
		|| !this.element.is(':visible')) {
			this._repaint(250);//TODO default interval here? separate option?
			return;
		}
		
		s = w < h ? w : h;
		u = Math.max(1, this._scale(s, this.options.padding));
		s = Math.max(s - u - u, 0);
		gx = ((w - s)/2) | 0;
		gy = ((h - s)/2) | 0;
		
		// repaint background if necessary
		if (w != this.width || h != this.height) {
			c = this.element.get(0).getContext('2d');
			$.extend(this, {size: s, width: w, height: h});
			
			// background
			this._style(c, s, 'ground', 0, 0, 0, h);
			c.fillRect(0, 0, w, h);
			c.strokeRect(0, 0, w, h);
			
			// face
			this._face(c, s, w, h, gx, gy);
			
			this.backdrop = c.getImageData(0, 0, w, h); // TODO tighten box
			this.repaint = true;
		}
		
		// repaint features if necessary
		if (this.repaint) {
			c = c || this.element.get(0).getContext('2d');
			this.repaint = false;
			c.putImageData(this.backdrop, 0, 0, 0, 0, w, h); // TODO tighten box
			
			// TODO improve performance if we pre-compute some common s/X below?
			
			this._updateFeatures();
			
			// "base" dimensions of eyes and mouth
			bew = s/4;
			beh = s/12;
			bmw = s/2;
			bmh = s/6;
			
			// offset to follow mouse cursor
			cx = this._clip((this.mouseX || w/2) - w/2, -w, w) / 20;
			cy = this._clip((this.mouseY || h/2) - h/2, -h, h) / 20;
			
			// features within face
			fx = cx + gx;
			fy = gy + s/10 - ((this.state.arousal + this.state.dominance) * s/20);
			
			// left eye
			ew = bew;
			eh = (beh * (this.feats[0] + 1)) + 1;
			ex = fx + s*(3/20);
			ey = fy + s/3 - eh/2;
			
			// brow (relative to ex,ey)
			bs = (beh * (this.feats[1] + 1)/2) + beh/2 + 1;
			bo = (beh * -this.feats[2])/2;
			bi = (beh * -this.feats[3])/2;
			
			// mouth
			mw = bmw * (this.feats[4] + 1)/6 + bmw/2;
			mh = bmh * (this.feats[5] + 1)/3;
			mt = (bmh * this.feats[6])/2;
			mx = fx + s/2 - mw/2;
			my = fy + s*(2/3) - mt;
			mu = mh - mt;
			ml = mh + mt;
			
			// teeth
			tv = bmh * (this.feats[7] - 1)/3;
			
			// paint eye/brows
			for (var k = 0; k < 2; k++) {
				this._eye(c, s, ex, ey, ew, eh);
				c.save();
				c.clip();
				this._iris(c, s, cx, cy, ex, ey, ew, eh);
				this._pupil(c, s, cx, cy, ex, ey, ew, eh);
				c.restore();
				this._brow(c, s, ex, ey, ew, eh, bs, bi, bo, k);
				ex = fx + s * (6/10);
			}
			
			// paint mouth
			// TODO split up in functions, as above:
			
			// draw shape, fill with teeth color, or shadow if enabled
			this._mouth(c, s, mx, my, mw, mu, ml);
			c.fillStyle = this.options.teeth.shadow || this.options.teeth.fill0;
			c.fill();
			// clip to mouth shape
			c.save();
			c.clip();
			if (this.options.teeth.shadow) {
				// if enabled, cover shadow with teeth color 
				this._mouth(c, s, mx + mh/5, my + mh/3, mw, mu, ml);
				c.fillStyle = this.options.teeth.fill0;
				c.fill();
			}
			// draw the grid of teeth (non-uniform, suggests a bit of a depth?)
			this._style(c, s, 'teeth');
			$.each(this.options.teeth.grid, function(kk, vv) {
				c.beginPath();
				c.moveTo(mx + vv*mw, Math.min(my, my - mu));
				c.lineTo(mx + vv*mw, Math.max(my, my + ml));
				c.closePath();
				c.stroke();
			});
			if (tv == 0) {
				// if teeth clenched, draw line in grid color
				c.moveTo(mx, my + mt);
				c.lineTo(mx + mw, my + mt);
				c.stroke();
			} else {
				// otherwise fill mouth
				this._style(c, s, 'mouth'
						, mx + mw/2, my + mh, mw/6
						, mx + mw/2, my + mh/2, mw/2);
				c.fillRect(mx, my + mt + tv, mw, -2*tv);
			}
			c.restore();

			// ugly.. need to do mouth shape again to paint lips
			this._mouth(c, s, mx, my, mw, mu, ml);
			this._style(c, s, 'mouth');
			c.stroke();
		}
		
		// schedule next (potential) repaint
		if (this.active) {
			this._repaint(this.options.interval - (Date.now() - t));
		}
	},
	
	_repaint: function(t) {
		var thiz = this;
		this.timer = window.setTimeout(function() { thiz._paint(); }, t);
	},
	
	_face: function(c, s, w, h, gx, gy) {
		c.beginPath();
		c.moveTo(gx, gy + s/3);
		c.bezierCurveTo(gx, gy + s/7, gx + s/6, gy, w/2, gy);
		c.bezierCurveTo(w - gx - s/6, gy, w - gx, gy + s/7, w - gx, gy + s/3);
		c.lineTo(w - gx, h/2);
		c.bezierCurveTo(w - gx, h - gy-s/3, w - gx - s/6, h - gy, w/2, h - gy);
		c.bezierCurveTo(gx + s/6, h - gy, gx, h - gy - s/3, gx, h/2);
		c.lineTo(gx, gy + s/3);
		c.closePath();
		this._style(c, s, 'face', w/2 - s/4, h/2 - s/7, s/4, w/2, h/2, s);
		this._shadow(c, s, 'face', true);
		this._shadow(c);
		c.fill();
		c.stroke();
	},
	
	_eye: function(c, s, ex, ey, ew, eh) {
		c.beginPath();
		c.moveTo(ex, ey + eh/2);
		c.bezierCurveTo(ex, ey + eh/4, ex + ew/6, ey, ex + ew/2, ey);
		c.bezierCurveTo(ex + ew - ew/6, ey, ex + ew, ey + eh/4, ex + ew, ey + eh/2);
		c.bezierCurveTo(ex + ew, ey + eh - eh/4, ex + ew - ew/6, ey + eh, ex + ew/2, ey + eh);
		c.bezierCurveTo(ex + ew/6, ey + eh, ex, ey + eh - eh/4, ex, ey + eh/2);
		c.closePath();
		this._style(c, s, 'eye');
		c.fill();
		c.stroke();
	},
	
	_iris: function(c, s, cx, cy, ex, ey, ew, eh) {
		c.beginPath();
		c.arc(cx + ex + ew/2, cy + ey + eh/2, ew/4, 0, 2*Math.PI);
		c.closePath();
		this._style(c, s, 'iris'
				, cx + ex + ew/2, cy + ey + eh/2, ew/10
				, cx + ex + ew/2, cy + ey + eh/2, ew/4); 
		c.fill();
		c.stroke();
	},
	
	_pupil: function(c, s, cx, cy, ex, ey, ew, eh) {
		c.beginPath();
		c.arc(cx + ex + ew/2, cy + ey + eh/2, ew/10, 0, 2*Math.PI);
		c.closePath();
		this._style(c, s, 'pupil');
		c.fill();
		c.stroke();
	},
	
	_brow: function(c, s, ex, ey, ew, eh, bs, bi, bo, k) {
		c.beginPath();
		c.moveTo(ex, ey + eh/2 - bs + (k ? bi : bo) - (bi-bo)/8);
		c.lineTo(ex + ew, ey + eh/2 - bs + (k ? bo : bi));
		c.closePath();
		this._shadow(c, s, 'brow');
		this._style(c, s, 'brow');
		c.stroke();
		this._shadow(c);
	},
	
	_mouth: function(c, s, mx, my, mw, up, lo) {
		c.beginPath();
		c.moveTo(mx, my);
		c.bezierCurveTo(mx, my - up/2, mx + mw/4, my - up, mx + mw/2, my - up);
		c.bezierCurveTo(mx + mw - mw/4, my - up, mx + mw, my - up/2, mx + mw, my);
		c.bezierCurveTo(mx + mw, my + lo/2, mx + mw - mw/4, my + lo, mx + mw/2, my + lo);
		c.bezierCurveTo(mx + mw/4, my + lo, mx, my + lo/2, mx, my);
		c.closePath();
	},
	
	_shadow: function(c, s, f, b) {
		if (arguments.length == 1) {
			c.shadowColor = '';
			c.shadowOffsetX = 0;
			c.shadowOffsetY = 0;
			c.shadowBlur = 0;
		} else {
			c.shadowColor = this.options[f]['shadow'];
			c.shadowOffsetX = this._scale(s, this.options[f].shadowX);
			c.shadowOffsetY = this._scale(s, this.options[f].shadowY);
			c.shadowBlur = b ? c.shadowOffsetX + c.shadowOffsetY : 0;
		}
	},
	
	_style: function(c, s, f) {
		var c0 = this.options[f].fill0,
			c1 = this.options[f].fill1 || c0,
			g;
		c.lineWidth = this._scale(s, this.options[f].width);
		c.strokeStyle = this.options[f].stroke;
		if (arguments.length > 3 && c0 != c1) {
			g = c['create' + (arguments.length > 7 ? 'Radial' : 'Linear') + 'Gradient']
					.apply(c, Array.prototype.slice.call(arguments, 3));
			g.addColorStop(0, c0);
			g.addColorStop(1, c1);
		} else {
			g = c0;
		}
		c.fillStyle = g;
	},
	
	_scale: function(s, r) {
		s = this._clip(s, this.options.scaleMin, this.options.scaleMax);
		return (r * s) / 100;
	},
	
	_clip: function(x, m, n) {
		m = m || -1;
		n = n || 1;
		return x < m ? m : x > n ? n : x;
	}

}); // end widget

})(jQuery, this); // end plugin
