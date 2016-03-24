/* COMPEIT */
/*Information Agent v0.1*/
/* Contributors: Harold T Nefs, Iulia Lefter, Tjerk de Greef*/


function InformationAgent(){
	 	var audioStream				= null;
		var canvasID				= document.createElement("canvas");
		canvasID.width 				= 640;
		canvasID.height 			= 480;
		var clientInfo				= {};
		var clientIP 				= null;
		var connectionAgent			= null;
		var context 				= canvasID.getContext('2d');
		//var pre_post_url 			= "/PHP/"
		var ia_url 					= "http://prototype.compeit.eu:9004/"		
		var pre_post_url 			= ia_url + "PHP/"
		
		var audioContext 			= new webkitAudioContext();
		var mytimer					= null;
		var myLocationTimer			= null;
		var mySnapSoundTimer		= null;
		newActivityHandler 			= function(){};		
		newMoodHandler 				= function(){};		
		newSnapLocationHandler 		= function(){};
		newSnapShotHandler 			= function(){};
		newSnapSoundHandler 		= function(){};
		var self 					= this;
		var snapShot				= false;
		var snapSound				= false;
		var srcID 					= null;
		var startedFlag				= false;
		var storageLocation 		= "";
		var snapLocationInterval	= 5*60*1000;
		var snapLocations			= [];
		var snapShotInterval		= 5*60*1000; //milliseconds  //5 minutes
		var snapSoundInterval		= 5*60*1000;
		var snapSoundDuration		= 5000;  //milliseconds
		var snapShotBrowser			= null;
		var privacySettings			= {
			"family": {"myAgenda": false, "myMood": false, "myLocation": false ,"myPhotos": false},
			"friends": {"myAgenda": false, "myMood": false, "myLocation": false, "myPhotos": false},
			"students": {"myAgenda": false, "myMood": false, "myLocation": false, "myPhotos": false},
			"teachers": {"myAgenda": false, "myMood": false, "myLocation": false, "myPhotos": false},
			"medstaff": {"myAgenda": false, "myMood": false, "myLocation": false, "myPhotos": false}	
			};
		var inCircleList			= {
			"familyCircle": "nobody",
			"friendsCircle": "",
			"studentsCircle": "",
			"teachersCircle":"",
			"medstaffCircle":""
		};
		var userInfo				= {};	
		var userLocation 			= {
			"timestamp":1,
			"coords": {"speed":0,"heading":0,"altitudeAccuracy":0,"accuracy":0,"altitude":0,"longitude":0,"latitude":0}};
		var mediaStreamSource 		= null; 	
			
	//PUBLIC methods
	this.changePrivacySetting = function(divID){
		var dest = privacySettings[divID.id.split(".")[0]][divID.id.split(".")[1]];
		dest != null?privacySettings[divID.id.split(".")[0]][divID.id.split(".")[1]] = divID.checked:0;
		$.post(pre_post_url + "/savePrivacy.php",{
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
	this.getSnapLocations			= function(){return snapLocations;};
	
	this.setURL             = function(url){ia_url = url; pre_post_url = ia_url + "PHP/"};
	this.getURL             = function(){return ia_url};
	
	this.infoRequestHandler			= function(event){ console.log(event); };  //hanlder for request and/or messages from remote informationAgents.
	
	
	//	IMPORTANT TODO: hide storage location!!!  same for the snapshots!
	this.playLastSnapSoundNow		= function(playerID){
		playerID.src = ia_url + "USERdataFOLDERwithAverySECRETname/" + storageLocation + "snapsounds/uploaded_audio.wav"
		console.log("playing audio");
		 };

	this.setConnectionAgent			= function(objValue){
		connectionAgent = objValue;
		};
	
	this.setPrivacyBrowser			= function(divID){
		privacyBrowser = divID;//TODO: not functional yet
		
		
		$.post(pre_post_url+"getPrivacy.php", {str : storageLocation + "privacy/"})
			 .done(function( data ) {
				console.log("object" + data);
				var dat =JSON.parse(data);
				for(var i in dat){
					for(var j in dat[i]){
						var datElem = document.getElementById(i + "." + j);
						datElem!=null ? datElem.checked = dat[i][j]:0;
						privacySettings[i][j] = dat[i][j]; 
					
						}
					}
				}
			);
		};
	
	this.setCircleList				= function(divID)
	{
		console.log("---Start function setCircleList");
		$.post(pre_post_url+"getCircles.php", {str : storageLocation + "inCircles/"})
			 .done(function( data ) 
			 {
				var dat = JSON.parse(data);
				console.log("inCircles\inCirclesList object" + data);
				for(var i in dat)
				{
					console.log("----"+i);//+"."+j);
					console.log("-----"+dat[i]);//[j]);
					var datElem = document.getElementById(i);
					datElem!=null?datElem.innerHTML = dat[i]:0; 
					inCircleList[i] = dat[i];
				}
				console.log("---End function setCircleList");
			 }
			);
		

		
	};

	
	this.setNewSnapLocationHandler			= function(clbck){newSnapLocationHandler = clbck; };
	this.setNewSnapShotHandler				= function(clbck){newSnapShotHandler = clbck; };
	this.setNewSnapSoundHandler				= function(clbck){newSnapSoundHandler = clbck; };
	this.setNewMoodHandler					= function(clbck){newMoodHandler = clbck; };
	this.setNewActivityHandler				= function(clbck){newActivityHandler = clbck; };
	this.setSnapLocation					= function(boolValue){
		snapLocation = boolValue;
		console.log("set snapLocation to: " + boolValue);
		if(snapLocation && startedFlag){
			takeSnapLocation();
			myLocationTimer =  setInterval(function(){takeSnapLocation()}, snapLocationInterval);
			}
		else{
			clearInterval(myLocationTimer);
			}
		};
		
	
	
	this.setSnapLocationInterval			= function(intValue){snapLocationInterval = intValue || snapLocationInterval;};
	this.setSnapLocationBrowser				= function(divID){}; // todo: needs to goto the demo
	this.setSnapShot						= function(boolValue){
		snapShot = boolValue;
		console.log("set snapshots to: " + boolValue);
		if(snapShot && startedFlag){
			srcID?takeSnapShot(srcID):0;
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
				img.src = ia_url + "IMG/favicon.ico";
				img.width= 40;
				img.height = 30;
				snapShotBrowser.appendChild(img);
				};
			refreshSnapShots();
		};
	
	this.setSnapShotInterval				= function(intvalue){ snapShotInterval  = intValue; };			
	this.setSnapShotSource 					= function(src){ srcID = src;};
	
	this.setSnapSound						= function(boolValue){
		console.log("set soundsnaps to: " + boolValue);
		snapSound = boolValue;
		if(snapSound && startedFlag){
			mediaStreamSource!=null?takeSnapSound(mediaStreamSource):0;
			mySnapSoundTimer = setInterval(function(){mediaStreamSource?takeSnapSound(mediaStreamSource):0;}, snapSoundInterval);
			}
		else{
			clearInterval(mySnapSoundTimer);
			};
		};
	this.setSnapSoundSource					= function(stream){ 
		audioStream  = stream; 
		mediaStreamSource = audioContext.createMediaStreamSource(audioStream);
		};
			
	this.setStorageLocation 				= function(strValue){ storageLocation  = strValue;};
	this.start								= function(){ start(); };
	this.takeSnapLocationNow				= function(){
		console.log("taking snaplocation now");
		takeSnapLocation();
		};
		
	this.takeSnapShotNow					= function(src){ 
		src = src || srcID;
		console.log("taking snapShot now");
		takeSnapShot(src); 
		};
	
	this.takeSnapSoundNow					= function(stream){
		console.log("taking snapsound now");
		takeSnapSound(mediaStreamSource);
		//mediaStreamSource=null;
		};
		
		
	
	//PRIVATE methods
	
	//HTN: These get functions may need to be expanded to include a start/end date, etc.
	
	function getLastNSnapShots(intValue){
		//this function will replace the refreshsnapshots, for getting image data
		};
		
	function getSnapLocations(){							
		$.post(pre_post_url+"getSnapLocations.php",{
				str: storageLocation + "snaplocations/"
				})
				.done(function( data ) {
					snapLocations = JSON.parse(data); 
				})
		};
	
		
	function newDataHandler(evt){
		console.log("kind" + evt.detail);
				switch (evt.detail.kind) {
			case "audio":
				newSnapSoundHandler(evt);
				updateMood(evt);
				break;
			case "ip":
				break;
			case "location":
				getSnapLocations();		//update from file
				newSnapLocationHandler(evt);
				break;
			case "snapShot":
				newSnapShotHandler(evt);
				refreshSnapShots();
				break;
			default: break;
			};
		};

		
	function newPredictionHandler(evt){
		console.log("event received:" + evt.detail.kind);
		switch (evt.detail.kind){
			case "activity":
				newActivityHandler(evt);
				break;
			case "mood":
				console.log("mood event received:" + JSON.stringify(evt.detail.data) );
				newMoodHandler(evt);
				break;
			default: 
				break;
			};
		};
	
	//TODO: IMPORTANT this reveals the location of the user data!!!
	function refreshSnapShots(){
		$.post(pre_post_url + "getSnapShots.php", {str : storageLocation + "snapshots/"})
			 .done(function( data ) {
				 var dat = JSON.parse(data);
				 for (var i=0; i<24; i++){	//last 24 images	
					(dat[dat.length -24 + i]!=null)?snapShotBrowser.childNodes[i].src = ia_url + dat[dat.length -24 + i]:0;
					};
				}
			);
		};
	
	
	function start(){
		startedFlag = true;
		// connectionAgent.broadCastInfo( make myself (IA) known) //msg.type must be "info";
		document.addEventListener("newDataAvailable", function(evt){newDataHandler(evt);} );
		document.addEventListener("newPredictionAvailable", function(evt){newPredictionHandler(evt);} );	
		getSnapLocations();
		$.get(pre_post_url + "getIP.php", 
			function(ip){
				clientIP = ip;
				document.getElementById("ip-address").innerHTML = clientIP;
				}
			);
		/*$.get("../PHP/getUserInfo.php", //this must be a "$.post". thought, maybe we should not retrieve the data for other users, but ask their informationAgents to send it to us!. 
			function(info){
				userInfo = info;		//personal details from the MYSQL database
				}
			);*/	
		};
	
	
	function takeSnapLocation(){
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(
				function (position) {
					userLocation = position || userLocation ;
					$.post(pre_post_url+"saveSnapLocation.php",{
						loc: JSON.stringify(userLocation),
						str: storageLocation + "snaplocations/"
						})
						.done(function( data ) {
							console.log("snapLocation saved to server with response: " + data);
							document.dispatchEvent( new CustomEvent("newDataAvailable", {detail:{kind: "location", data: userLocation}})); 				
							}
						);
					}
				);
			};	
		};
		
		
	function takeSnapShot(src){
		console.log("take snapshot "+src);
		if(src){
			context.drawImage(src, 0,0, 640,480);
			var dataURL = canvasID.toDataURL('image/jpeg',0.5);
			$.post(pre_post_url + "saveSnapShot.php",{
				img: dataURL,
				str: storageLocation + "snapshots/"
				})
				.done(function( data ) {
					console.log("snapshot saved as: " + data );
					document.dispatchEvent( new CustomEvent("newDataAvailable", {'detail':{'kind':"snapShot", data: {}}}));					
					}
				);
			};
		};
		
	
		
	function takeSnapSound(mediaStreamSource){
		if(mediaStreamSource){
            var recorder = new Recorder(mediaStreamSource);
            console.log("start audio recording");
			recorder.record();
			setTimeout(function(){
				recorder.stop();
				console.log("stop audio recording");
				recorder.exportWAV(function(blob){
					var tmpfile = new FileReader();
					tmpfile.onloadend = function(e){				 
						$.post(pre_post_url + "uploadWAV.php",{
							data: tmpfile.result,
							str: storageLocation + "snapsounds/"
							})
							.done(function( data ) {
								console.log("snapsound saved as: " + data );
								document.dispatchEvent( new CustomEvent("newDataAvailable", {'detail':{'kind': "audio", 'data': {}}})); 
								})
						};
					tmpfile.readAsDataURL( blob );
					})
				}
				, snapSoundDuration);
            };
		};	
	
		
	function updateMood(evt){
		$.post(ia_url + "InformationAgent/php/call_praat.php",{
			str: storageLocation + "snapsounds/"
			})
			.done(function(data){
				//todo: save the new mood to a logfile
				console.log("received from PRAAT" + data);
				document.dispatchEvent( new CustomEvent("newPredictionAvailable", {'detail': {'kind': "mood", 'data': JSON.parse(data)}})); 
				});
        };
	
	}; //end of InformationAgent
//end of file


	
	


