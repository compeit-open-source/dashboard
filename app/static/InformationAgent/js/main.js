/* COMPEIT: demo InformationAgent v.0.1 
main.js
This demo code shows how to use the InformationAgent object.
Contributors: Iulia Lefter, Harold T Nefs, Tjerk de Greef
*/


function InformationAgentModule(storageLocation){
	//PRIVATE
	var informationAgent 		= new InformationAgent();
	
	//PUBLIC methods
	this.changePrivacySetting 	= function(divID){informationAgent.changePrivacySetting(divID);};
	this.takeSnapSoundNow 		= informationAgent.takeSnapSoundNow;
	this.takeSnapShotNow 		= informationAgent.takeSnapShotNow;
	this.playLastSnapSoundNow 	= function(){ informationAgent.playLastSnapSoundNow( document.getElementById("audioplayer"));};
	
	this.setURL             = informationAgent.setURL;
	this.getURL             = informationAgent.getURL;

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
	
	console.log('storageLocation: ' + storageLocation)

	//LOAD and RUN				
	informationAgent.setNewSnapLocationHandler(newSnapLocationHandler);
	informationAgent.setNewMoodHandler(newMoodHandler);
	informationAgent.setStorageLocation(storageLocation+'/'); 
	informationAgent.setSnapShotBrowser( document.getElementById("snapShotBrowser")); 
	
	informationAgent.setPrivacyBrowser("");
	informationAgent.setCircleList("");
					
    $('body').on('localMedia', function(event, videoContainer, stream) {
    	console.log('videoContainer:' + videoContainer)
    	console.log('stream:' + stream)
		informationAgent.setSnapShotSource( videoContainer );
		informationAgent.setSnapSoundSource(stream);
		informationAgent.setSnapShot(true);
		informationAgent.setSnapLocation(true);
		informationAgent.setSnapSound(true);
	});

	informationAgent.start();	

};

		
    
	      
        
	


