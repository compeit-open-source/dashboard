/* COMPEIT: demo InformationAgent v.0.1 
main.js
This demo code shows how to use the InformationAgent object.
Contributors: Iulia Lefter, Harold T Nefs, Tjerk de Greef
*/


function Demo(){
	//PRIVATE
	var informationAgent 		= new InformationAgent();
	var connectionAgent 		= new ConnectionAgent();
	
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
	informationAgent.setStorageLocation("59492717/"); 
	informationAgent.setSnapShotBrowser( document.getElementById("snapShotBrowser")); 
	
	informationAgent.setPrivacyBrowser("");
	informationAgent.setCircleList("");
	
	document.addEventListener('getUserMediaSuccess', function(evt){
			informationAgent.setSnapShotSource( document.getElementById("videoContainer").firstChild );
			informationAgent.setSnapSoundSource(connectionAgent.getLocalStream());
			informationAgent.setSnapShot(true);
			informationAgent.setSnapLocation(true);
			informationAgent.setSnapSound(true);
			}
		);
	informationAgent.setConnectionAgent(connectionAgent);	//this is still general, we may want to set this to be a more specific call back int he connectionAgent
	
	connectionAgent.setRoom(3421);
	connectionAgent.setVideoContainer(document.getElementById("videoContainer"));
	connectionAgent.onRemoteInfo(informationAgent.infoRequestHandler);  //if the connectionAgent wants something, it activates this callback with a "message object"

	connectionAgent.start();
	informationAgent.start();	

};

		
    
	      
        
	


