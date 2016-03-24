/* COMPEIT: demo InformationAgent v.0.1 
main.js
This demo code shows how to use the InformationAgent object.
Contributors: Iulia Lefter, Harold T Nefs, Tjerk de Greef
*/


function Demo(storageLocation){
	//PRIVATE
	var informationAgent 		= new InformationAgent();
	
	//PUBLIC methods
	this.changePrivacySetting 	= function(divID){informationAgent.changePrivacySetting(divID);};
	this.takeSnapSoundNow 		= informationAgent.takeSnapSoundNow;
	this.takeSnapShotNow 		= informationAgent.takeSnapShotNow;
	this.playLastSnapSoundNow 	= function(){ informationAgent.playLastSnapSoundNow( document.getElementById("audioplayer"));};
	
	//PRIVATE
	function newSnapLocationHandler(evt){
		var position = evt.detail.data;
		document.getElementById("location").innerHTML="Latitude: " + position.coords.latitude + 
    			"<br>Longitude: " + position.coords.longitude;
				var myLatlng= new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
				setTimeout(function(){map.setCenter(myLatlng);
				new google.maps.Marker({ position: myLatlng, map: map, title: 'I am here!'});}, 3000);
			};
	
	
	function newMoodHandler(evt){
		document.getElementById('pleasure').value = evt.detail.data.pleasure;
		document.getElementById('arousal').value = evt.detail.data.arousal;
		document.getElementById('dominance').value = evt.detail.data.dominance;
		$('#affect').affectbutton('affect', 'pleasure', evt.detail.data.pleasure);
		$('#affect').affectbutton('affect', 'arousal', evt.detail.data.arousal);
		$('#affect').affectbutton('affect', 'dominance', evt.detail.data.dominance);
		
		
		};
		
	function newSnapShotHandler(evt){
	// handle the new snapshot
		};
	
	//LOAD and RUN				
	informationAgent.setNewSnapLocationHandler(newSnapLocationHandler);
	informationAgent.setNewMoodHandler(newMoodHandler);
	informationAgent.setStorageLocation(storageLocation+"/"); 
	informationAgent.setSnapShotBrowser( document.getElementById("snapShotBrowser")); 
	
	informationAgent.setPrivacyBrowser("");
	informationAgent.setCircleList("");
					
	function onUserMediaSuccess(stream) {
		localStream = stream;
		localVid = document.createElement('video');
		localVid.src = webkitURL.createObjectURL(stream);
		localVid.width= 320;
		localVid.height= 200;
		$('#videoContainer').append(localVid);
		localVid.play();
		localVid.setAttribute('muted', true);

		informationAgent.setSnapShotSource( document.getElementById("videoContainer").firstChild );
		informationAgent.setSnapSoundSource(stream);
		informationAgent.setSnapShot(true);
		informationAgent.setSnapLocation(true);
		informationAgent.setSnapSound(true);
	};

	function onUserMediaError(error) {
		alert("Failed to get access to local media. Error code was " + error.code + ".");
	};

	try {	
		navigator.webkitGetUserMedia({audio: true, video: true}, onUserMediaSuccess, onUserMediaError);
	} catch (e) {
		alert("webkitGetUserMedia() failed. Is the MediaStream flag enabled in about:flags?");
		console.log("webkitGetUserMedia failed with exception: " + e.message);
	};

	informationAgent.start();	

};

		
    
	      
        
	


