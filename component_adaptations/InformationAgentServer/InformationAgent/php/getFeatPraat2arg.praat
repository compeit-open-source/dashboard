  	#fara toate featureurile de la duration si cu max f0 si max intensity. la ltas fara pitch corrected ca nu merge la toate fisierele
	
	form Get arguments
		word filename
		word outfile
	endform
	

#	printline 'filelist$'

	output$ =""
	length=length(filename$)
	nrchar=length - 4
	
#	outfile$ = left$(filename$,nrchar)+".feat"
	printline 'outfile$'
	filedelete 'outfile$'
	
	Read from file... 'filename$'
	Rename... sound

	length=length(filename$)
	nrchar=length - 4
	
#	outfile$ = "FEAT/"+left$(filename$,nrchar)+".feat"
	filedelete 'outfile$'
	outfile2$="TAB/"+left$(filename$,nrchar)+".tab"
	filedelete 'outfile2$'
	
	Read from file... 'filename$'
  Rename... sound
  
  ##################################################################################################
  #get grid with silences and sound intervals, then extract the sound and silence intervals and concatenate them
  ##################################################################################################
  select Sound sound
  To Intensity... 100 0 yes
  To TextGrid (silences)... -20 0.1 0.1 silent sounding
  
  #----------------------get the total duration of sound and silence intervals
  select TextGrid sound
  nsil=Count labels... 1 silent
  nsound=Count labels... 1 sounding
  
  durSound=0
  if nsound!=0
	  select Sound sound
	  plus TextGrid sound
	  Extract intervals where... 1 no "is equal to" sounding
	  Concatenate
	  Rename...  soundChain
	  durSound=Get total duration
  endif
  
   durSil=0
  if nsil!=0
    select Sound sound
    plus TextGrid sound
    Extract intervals where... 1 no "is equal to" silent
    Concatenate
    Rename...  silChain
    durSil=Get total duration
  endif
  
  printline 'durSound:5'
  ########################################################################################
  #----------continue with the sound without pauses & extract the old feature set...
  ########################################################################################
  
  #select Sound sound
  #Remove
  if nsil!=0
	  for i from 1 to nsil
		nr$=fixed$(i,0)
		name$="sound_silent_"+nr$
		select Sound 'name$'
		Remove
	  endfor
  endif
  if nsound!=0
	  for i from 1 to nsound
		nr$=fixed$(i,0)
		name$="sound_sounding_"+nr$
		select Sound 'name$'
		Remove
	  endfor
  endif
  if nsil!=0
    select Sound silChain
    Remove
  endif
  #select Sound soundChain
  #Rename... sound

#----------------------------------------------------------------------------------------------
# ---------get pitch related features (mean, standar dev., range, absolute slope 
#----------------------------------------------------------------------------------------------

	select Sound sound
	To Pitch... 0.0 75.0 600.0
	Rename... pitch
	mpitch=Get mean... 0.0 0.0 Hertz
	sdpitch=Get standard deviation... 0.0 0.0 Hertz
	maxpitch=Get maximum... 0.0 0.0 Hertz Parabolic
	minpitch=Get minimum... 0.0 0.0 Hertz Parabolic
	rangepitch=maxpitch-minpitch
	
	meanabsslope=Get mean absolute slope... Hertz
	meanslopeoct=Get slope without octave jumps
	
	maxpitch$ = fixed$ (maxpitch, 5)
	if maxpitch$ = "--undefined--"
	   maxpitch = 0
	endif
	
	minpitch$ = fixed$ (minpitch, 5)
	if minpitch$ = "--undefined--"
	   minpitch = 0
	endif
	
	mpitch$ = fixed$ (mpitch, 5)
	if mpitch$ = "--undefined--"
	   mpitch = 0
	endif
	sdpitch$ = fixed$ (sdpitch, 5)
	if sdpitch$ = "--undefined--"
	   sdpitch = 0
	endif
	rangepitch$ = fixed$ (rangepitch, 5)
	if rangepitch$ = "--undefined--"
	   rangepitch = 0
	endif
	meanabsslope$ = fixed$ (meanabsslope, 5)
	if meanabsslope$ = "--undefined--"
	   meanabsslope = 0
	endif
	meanslopeoct$ = fixed$ (meanslopeoct, 5)
	if meanslopeoct$ = "--undefined--"
	   meanslopeoct = 0
	endif

	
	#output$ = output$ + mpitch:5 + 'sdpitch:5' + 'rangepitch:5' + 'meanabsslope:5' + 'meanslopeoct:5' 

#----------------------------------------------------------------------------------------------
#------check if duration >= 6.4/minPitch, otherwhise To intensity... cannot be performed, so exit 0
#----------------------------------------------------------------------------------------------
	
	select Sound sound
	duration = Get total duration
	if (minpitch != 0)
		thres=6.4/minpitch
		if (duration < thres)
			exit
		endif
	endif
	
#----------------------------------------------------------------------------------------------
#----- get intensity related features (mean, standar dev., range, mean slope 
#----------------------------------------------------------------------------------------------

	select Sound sound
	To Intensity... 100 0.0 yes
	Rename... intensity
	mintens=Get mean... 0.0 0.0 energy
	sdintens=Get standard deviation... 0.0 0.0
	maxintens=Get maximum... 0.0 0.0 Parabolic
	minintens=Get minimum... 0.0 0.0 Parabolic
	rangeintens=maxintens-minintens

	nvalj=0
	totvalj=0
	nframe=Get number of frames
	for j from 1 to nframe
		select Intensity intensity
		valj=Get value in frame... 'j'
		if (valj=undefined)
		else
	   	totvalj=totvalj+valj	
	   	nvalj=nvalj+1
		endif
	endfor
	meanslopeintens=totvalj/nvalj

	mintens$ = fixed$ (mintens, 5)
	if mintens$ = "--undefined--"
	   mintens = 0
	endif
	
	maxintens$ = fixed$ (maxintens, 5)
	if maxintens$ = "--undefined--"
	   maxintens = 0
	endif
	
	sdintens$ = fixed$ (sdintens, 5)
	if sdintens$ = "--undefined--"
	   sdintens = 0
	endif
	rangeintens$ = fixed$ (rangeintens, 5)
	if rangeintens$ = "--undefined--"
	   rangeintens = 0
	endif
	meanslopeintens$ = fixed$ (meanslopeintens, 5)
	if meanslopeintens$ = "--undefined--"
	   meanslopeintens = 0
	endif
	
	
	
	
	
	#########################
	# get formant information
	#########################

	select Sound sound
	To Formant (burg)... 0 4 5500 0.1 50
	Rename... formant

	select Formant formant
	meanF1 = Get mean... 1 0 0 Hertz
	meanF1$ = fixed$ (meanF1, 5)
	
	if meanF1$ = "--undefined--"
	   meanF1 = 0
	endif
	
	select Formant formant
	bw1=Get quantile of bandwidth... 1 0 0 Hertz 0.5
	bw1$ = fixed$ (bw1, 5)
	if bw1$ = "--undefined--"
	   bw1 = 0
	endif

	select Formant formant
	meanF2 = Get mean... 2 0 0 Hertz
	meanF2$ = fixed$ (meanF2, 5)

	if meanF2$ = "--undefined--"
	   meanF2 = 0
	endif
	
	select Formant formant
	bw2=Get quantile of bandwidth... 2 0 0 Hertz 0.5
	bw2$ = fixed$ (bw2, 5)
	if bw2$ = "--undefined--"
	   bw2 = 0
	endif

	select Formant formant
	meanF3 = Get mean... 3 0 0 Hertz
	meanF3$ = fixed$ (meanF3, 5)
	
	if meanF3$ = "--undefined--"
	   meanF3 = 0
	endif
	
	select Formant formant
	bw3=Get quantile of bandwidth... 3 0 0 Hertz 0.5
	bw3$ = fixed$ (bw3, 5)
	if bw3$ = "--undefined--"
	   bw3 = 0
	endif

	select Formant formant
	meanF4 = Get mean... 4 0 0 Hertz
	meanF4$ = fixed$ (meanF4, 5)

	if meanF4$ = "--undefined--"
	   meanF4 = 0
	endif
	
	select Formant formant
	bw4=Get quantile of bandwidth... 4 0 0 Hertz 0.5
	bw4$ = fixed$ (bw4, 5)
	if bw4$ = "--undefined--"
	   bw4 = 0
	endif

#----------------------------------------------------------------------------------------------
# get jitter, shimmer, high energy
#----------------------------------------------------------------------------------------------

	select Pitch pitch
	To PointProcess
	Rename... pointprocess

	select PointProcess pointprocess
	jitter=Get jitter (ddp)... 0 0 0.0001 0.02 1.3
	jitter$ = fixed$ (jitter, 5)

	if jitter$ = "--undefined--"
	   jitter = 0
	endif

	select Sound sound
	plus PointProcess pointprocess
	shimmer=Get shimmer (dda)... 0 0 0.0001 0.02 1.3 1.6
	shimmer$ = fixed$ (shimmer, 5)

	if shimmer$ = "--undefined--"
	   shimmer = 0
	endif
	
#----------------------------------------------------------------------------------------------
# get long term averaged spectrum features : high energy, slope, hammarberg index, center of gravity, skew
#----------------------------------------------------------------------------------------------	
	
	select Sound sound
	To Ltas... 100
	high_energy = Get mean... 0 0 energy
	
	high_energy$ = fixed$ (high_energy, 5)

	if high_energy$ = "--undefined--"
	   high_energy = 0
	endif

	select Ltas sound
	slopeltaspc=Get slope... 0.0 1000 1000 4000 energy
	maxlow=Get maximum... 0 2000 None
	maxhigh=Get maximum... 2000 5000 None
	hammari=maxlow-maxhigh

	slopeltaspc$= fixed$ (slopeltaspc, 5)
	if slopeltaspc$="--undefined--"
		slopeltaspc=0
	endif
	
	hammari$=fixed$ (hammari, 5)
	if hammari$="--undefined--"
		hammari=0
	endif
	



	select Sound sound
	To Spectrum... yes
	Rename... spectrum
	
	cog=Get centre of gravity... 2.0
	cog$=fixed$ (cog, 5)
	if cog$="--undefined--"
		cog=0
	endif
	
	skew=Get skewness... 2.0
	skew$=fixed$ (skew, 5)
	if skew$="--undefined--"
		skew=0
	endif
	
	select Spectrum spectrum
	lo=Get band energy... 200 500
	hi=Get band energy... 500 7000
	hf500=hi/lo
	hf500$=fixed$ (hf500, 5)
	if hf500$="--undefined--"
		hf500=0
	endif
	
	select Spectrum spectrum
	lo=Get band energy... 200 1000
	hi=Get band energy... 1000 7000
	hf1000=hi/lo
	hf1000$=fixed$ (hf1000, 5)
	if hf1000$="--undefined--"
		hf1000=0
	endif
	
	select Sound sound
	To Harmonicity (cc)... 0.01 75 0.1 1
	hnr=Get mean... 0 0
	hnr$=fixed$ (hnr, 5)
	if hnr$="--undefined--"
		hnr=0
	endif
	
	select Harmonicity sound
	stdhnr=Get standard deviation... 0 0
	stdhnr$=fixed$ (stdhnr, 5)
	if stdhnr$="--undefined--"
		stdhnr=0
	endif
	
#----------------------------------------------------------------------------------------------
# write features to file
#----------------------------------------------------------------------------------------------	

  fileappend 'outfile$' 'durSound:5' 
	fileappend 'outfile$' 'mpitch:5' 'maxpitch:5' 'sdpitch:5' 'rangepitch:5' 'meanabsslope:5' 'meanslopeoct:5' 
	fileappend 'outfile$' 'mintens:5' 'maxintens:5' 'sdintens:5' 'rangeintens:5' 'meanslopeintens:5' 
	fileappend 'outfile$' 'meanF1:5' 'meanF2:5' 'meanF3:5' 'meanF4:5' 
	fileappend 'outfile$' 'bw1:5' 'bw2:5' 'bw3:5' 'bw4:5' 
	fileappend 'outfile$' 'jitter:5' 'shimmer:5' 'high_energy:5' 'slopeltaspc:5' 'hammari:5' 'cog:5' 'skew:5' 'hf500' 'hf1000' 'hnr:5' 'stdhnr:5' 'newline$'
	
	select Sound sound
	Remove
	select Pitch pitch
	Remove
	select Intensity intensity
	Remove
	select Intensity sound
	Remove
	select PointProcess pointprocess
	Remove
	select TextGrid sound
	Remove
	select Formant formant
	Remove
	select Ltas sound
	Remove
	select Spectrum spectrum
	Remove
	select Harmonicity sound
	Remove
	select Sound sound
	Remove