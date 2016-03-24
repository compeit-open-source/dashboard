/* COMPEIT */
/*Information Agent v0.1*/
/* Contributors: Harold T Nefs, Iulia Lefter, Tjerk de Greef*/


function InformationAgent(){
	 	var audiostream				= null;
		var canvasID				= document.createElement("canvas");
		canvasID.width 				= 640;
		canvasID.height 			= 480;
		var clientInfo				= {};
		var clientIP 				= null;
		var context 				= canvasID.getContext('2d'); 
		var mytimer					= null;
		var myLocationTimer			= null;
		var mySnapSoundTimer		= null;
		newActivityHandler 			= function(){};		
		newMoodHandler 				= function(){};		
		newSnapLocationHandler 		= function(){};
		newSnapShotHandler 			= function(){};
		newSnapSoundHandler 		= function(){};
		var snapShot				= false;
		var snapSound				= false;
		var srcID 					= null;
		var storageLocation 		= "";
		var snapLocationInterval	= 5*60*1000;
		var snapShotInterval		= 5*60*1000; //milliseconds  //5 minutes
		var snapSoundInterval		= 5*60*1000;
		var snapSoundDuration		= 5000;  //milliseconds
		var snapShotBrowser			= null;
		var privacySettings			= {
			"family": {"myAgenda": true, "myMood": true, "myLocation": true ,"myPhotos": true},
			"friends": {"myAgenda": false, "myMood": true, "myLocation": false, "myPhotos": true},
			"students": {"myAgenda": false, "myMood": true, "myLocation": false, "myPhotos": true},
			"teachers": {"myAgenda": true, "myMood": false, "myLocation": false, "myPhotos": true},
			"medstaff": {"myAgenda": true, "myMood": true, "myLocation": true, "myPhotos": true}	
			};
		var userInfo				= {};	
		var userLocation 			= {"coords": {"latitude" : 0, "longitude": 0}};

			
	//PUBLIC methods
	this.changePrivacySetting = function(divID){
		var dest = privacySettings[divID.id.split(".")[0]][divID.id.split(".")[1]];
		dest != null?privacySettings[divID.id.split(".")[0]][divID.id.split(".")[1]] = divID.checked:0;
		$.post("../PHP/savePrivacy.php",{
			data: JSON.stringify(privacySettings),
			str: storageLocation + "privacy/"
			})
			.done(function( data ) {
				console.log("privacy saved as: " + data );
				});
		};
		
	this.getClientIP 				= function(){return clientIP;};
	this.getClientInfo				= function(){return userInfo;};
	this.getClientLocation 			= function(){return userLocation;};

	//	IMPORTANT TODO: hide storage location!!!  same for the snapshots!
	this.playLastSnapSoundNow				= function(playerID){
		playerID.src = "/USERdataFOLDERwithAverySECRETname/" + storageLocation + "snapsounds/uploaded_audio.wav"
		console.log("playing audio");
		 };

	this.setPrivacyBrowser					= function(divID){
		privacyBrowser = divID;//TODO: not functional yet
		$.post("../PHP/getPrivacy.php", {str : storageLocation + "privacy/"})
			 .done(function( data ) {
				var dat = JSON.parse(data);
				for(var i in dat){
					for(var j in dat[i]){
						var datElem = document.getElementById(i + "." + j);
						datElem!=null?datElem.checked = dat[i][j]:0;
						}
					}
				}
			);
		};
		
	this.setNewSnapLocationHandler			= function(clbck){newSnapLocationHandler = clbck; };
	this.setNewSnapShotHandler				= function(clbck){newSnapShotHandler = clbck; };
	this.setNewSnapSoundHandler				= function(clbck){newSnapSoundHandler = clbck; };
	this.setNewMoodHandler					= function(clbck){newMoodHandler = clbck; };
	this.setNewActivityHandler				= function(clbck){newActivityHandler = clbck; };
	this.setSnapLocation					= function(boolValue){
		console.log("set snapLocation to: " + boolValue);
		snapLocation = boolValue;
		if(snapLocation){
			myLocationTimer =  setInterval(function(){takeSnapLocation()}, snapLocationInterval);
			}
		else{
			clearInterval(myLocationTimer);
			}
		};
		
	this.setSnapLocationInterval			= function(intValue){};
	this.setSnapLocationBrowser				= function(divID){}; // todo: needs to goto the demo
	this.setSnapShot						= function(boolValue){
		snapShot = boolValue;
		srcID?takeSnapShot(srcID):0;
		console.log("set snapshots to: " + boolValue);
		if(snapShot){
			mytimer = setInterval(function(){srcID?takeSnapShot(srcID):0}, snapShotInterval);
			}
		else{
			clearInterval(mytimer);
			};
		};
		 
	this.setSnapShotBrowser					= function(divID){	 //TODO: this needs to go to the demo
			var img;
			snapShotBrowser	= divID;
			for (var i=0; i<24; i++){	 
				img = document.createElement("img");
				img.src = "/IMG/favicon.ico";
				img.width= 40;
				img.height = 30;
				snapShotBrowser.appendChild(img);
				};
			refreshSnapShots();
		};
	
	this.setSnapShotInterval			= function(intvalue){ snapShotInterval  = intValue; };			
	this.setSnapShotSource 				= function(src){ srcID = src };
	this.setSnapSoundSource				= function(stream){ audioStream  = stream; };
	
	this.setSnapSound					= function(boolValue){
		console.log("set soundsnaps to: " + boolValue);
		snapSound = boolValue;
		audioStream?takeSnapSound(audioStream):0;
		if(snapSound){
			mySnapSoundTimer = setInterval(function(){audioStream?takeSnapSound(audioStream):0;}, snapSoundInterval);
			}
		else{
			clearInterval(mySnapSoundTimer);
			};
		};
		
	this.setStorageLocation 			= function(strValue){ storageLocation  = strValue;};
	this.start							= function(){ start(); };
	this.takeSnapShotNow				= function(src){ 
		src = src || srcID;
		console.log("taking snapShot now");
		takeSnapShot(src); 
		};
	this.takeSnapLocationNow			= function(){
		console.log("taking snaplocation now");
		takeSnapLocation();
		};
	this.takeSnapSoundNow				= function(stream){
		stream = stream || audioStream;
		console.log("taking snapsound now");
		takeSnapSound(stream);
		};
		
	
	//PRIVATE methods
	getLastNSnapShots = function(intValue){
		//this function will replace the refreshsnapshots, for getting image data
		};
		
	function newDataHandler(evt){
		switch (evt.kind) {
			case "audio":
				updateMood(evt);
				break;
			case "ip":
				break;
			case "location":
				break;
			case "snapShot":
				refreshSnapShots();
				break;
			default: break;
			};
		};
	
		
	function newPredictionHandler(evt){
		switch (evt.kind){
			case "activity":
				break;
			case "mood":
				break;
			default: 
				break;
			};
		};
	
	//TODO: IMPORTANT this reveals the location of the user data!!!
	function refreshSnapShots(){
		$.post("../PHP/getSnapShots.php", {str : storageLocation + "snapshots/"})
			 .done(function( data ) {
				 var dat = JSON.parse(data);
				 for (var i=0; i<24; i++){	//last 24 images	
					(dat[dat.length -24 + i]!=null)?snapShotBrowser.childNodes[i+3].src = dat[dat.length -24 + i]:0;//HTN: don't know why +3
					};
				}
			);
		};
	
	
	function start(){
		document.addEventListener("newDataAvailable", function(evt){newDataHandler(evt);} );
		document.addEventListener("newPredictionAvailable", function(evt){newPredictionHandler(evt);} );	
		this.setSnapSound(snapSound);			//these will also trigger the first request for data, if set to true
		this.setSnapShot(snapShot);
		this.setSnapLocation(snapLocation);
		$.get("../PHP/getIP.php", 
			function(ip){
				clientIP = ip;
				console.log("clientIP  = " + clientIP);
				document.getElementById("ip-address").innerHTML = clientIP;
				}
			);
		$.get("../PHP/getUserInfo.php", 
			function(info){
				userInfo = info;		//personal details from the MYSQL database
				}
			);	
		
		};
	
	
	function takeSnapLocation(){
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(
				function (position) {
					userLocation = position || userLocation ;
					document.dispatchEvent( new CustomEvent("newDataAvailable", {"kind":"location"})); 
					}
				);
			};	
		};
	
		
	function takeSnapShot(src){
		console.log("take snapshot");
		if(src){
			context.drawImage(src, 0,0, 640,480);
			var dataURL = canvasID.toDataURL('image/jpeg',0.5);
			$.post("/PHP/saveSnapShot.php",{
				img: dataURL,
				str: storageLocation + "snapshots/"
				})
				.done(function( data ) {
					console.log("snapshot saved as: " + data );
					document.dispatchEvent( new CustomEvent("newDataAvailable", {"kind":"snapShot"}));					
					}
				);
			};
		};
		
	function takeSnapSound(stream){
		if(stream){
		   	var context = new webkitAudioContext();
            var mediaStreamSource = context.createMediaStreamSource(stream);
            var recorder = new Recorder(mediaStreamSource);
            console.log("start audio recording");
			recorder.record();
			setTimeout(function(){
				recorder.stop();
				console.log("stop audio recording");
				recorder.exportWAV(function(blob){
					var tmpfile = new FileReader();
					tmpfile.onloadend = function(e){				 
						$.post("/PHP/uploadWAV.php",{
							data: tmpfile.result,
							str: storageLocation + "snapsounds/"
							})
							.done(function( data ) {
								console.log("snapsound saved as: " + data );
								document.dispatchEvent( new CustomEvent("newDataAvailable", {"kind":"audio"})); 
								})
						};
					tmpfile.readAsDataURL( blob );
					})
				}
				, snapSoundDuration);
            };
		};	
	
		
	function updateMood(evt){
		/*TODO: call the moodMachine here*/	
			/*	$.post("php/call_SMILE.php")
				.done(function(data){console.log(data)});
            }*/
 		document.dispatchEvent( new CustomEvent("newPredictionaAvailable", {"kind":"mood"})); 
		};
	
	}; //end of InformationAgent
//end of file


	
	


