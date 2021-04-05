#Written by Raoul Nottrott, Project Autofocus, Basler AG 2015
#This module provides some peak finding algorithms

import time
import sys
import cv2
from autofocus import ContrastMeasures, go_to_position, resetPosition
# from camera import ScopeStream
try:
	from views import currentPosition
except:
	currentPosition = 0
# cam = ScopeStream(name='nameless',flowType="development")
if (currentPosition == 0):
	currentPosition = int(0)
def fibonacci_peak(cam,minZposition,maxZposition,hysteresis,tolerance,aoi = [0,0,2544,1922]):
	"""Fibonacci peak search taken from E. Krotkov: "Focusing" P.233
		returns -
			position(int) - autofocused
			complexity(int) - value 
			fibonacciLoopCount(int) - actual number of loops used(can try ways to reduce loops)
	"""
	#	cam: camera already opened - GrabOne(take photo)
	#	focus: focus from used LenseController - go_to_position
	#	ak: start step no. - 0
	#	maxZposition: stop step no. - 12000
	#	aoi: area of interest in form [x1,y1,x2,y2] - x-y complexity calculation (2544, 1922)
	#	hysteresis: offset to compensate hysteresis
	#	tolerance: tolerance limit, algorithm stops when the search interval becomes smaller than tolerance - step size limit ()
	currentPos = 0
	tmp1=0 #to check autofocus position
	loopCount =fibonacci(maxZposition)[1]	#calculate theoretical number of loops needed for peak finding
	fibonacciLoopCount=0			#variable to count actual number of loops used
	stepDir= "Forward" #indicates lense's step direction, 1: step forward, 0: step backward
					#(needed to compensate lense hysteresis depending on move direction)
	tmp2=0				#saves last position to detect move direction
	offset=0			#offset to add to actual position to compensate hysteresis, offset is 
					#either =hysteresis or 0-1*hysteresis depending on step direction
	fm = ContrastMeasures()
	for k in range(1,loopCount+1):
		fibonacciLoopCount+=1		#count loops

		if k==1:
			fibonacciRatio=maxZposition-minZposition #	fibonacciRatio - diff between the range of step size
		else:
			fibonacciRatio=fibonacciRatio*(float(fibonacci2(loopCount-k+1))/float(fibonacci2(loopCount-k+2))) #ratio of subsequent fibonacci series values

		goToPosition=fibonacciRatio*(float(fibonacci2(loopCount-k-1))/float(fibonacci2(loopCount-k+1))) #goToPosition - net go to position

		if k==1:						#first interval, lense always moves forward
			autoFocusedPositionA=int(round(minZposition+goToPosition)) #start + goToPosition
			currentPos = go_to_position(autoFocusedPositionA,currentPos) 
				# img=cam.GrabOne(1000).Array[aoi[1]:aoi[3],aoi[0]:aoi[2]] #take img
			img = cam.start_stream_object(1000)
			focusedPositionComplexityA=fm.fm(img,'TENENGRAD1',5,0).mean() #calc complecity
			autoFocusedPositionB=int(round(maxZposition-goToPosition)) #end - goToPosition
			currentPos = go_to_position(autoFocusedPositionB,currentPos)
			img = cam.start_stream_object(1000) #take img
			focusedPositionComplexityB=fm.fm(img,'TENENGRAD1',5,0).mean() #calc complecity
			tmp2=autoFocusedPositionB
				
		elif tmp1==1:
			autoFocusedPositionA=int(round(minZposition+goToPosition))		#calculate next position

			if autoFocusedPositionA>tmp2:				#determine moving direction, depending on direction, determine offset
				stepDir="Forward"
				offset=hysteresis		
			else:
				stepDir=0
				offset=-1*hysteresis
			tmp2=autoFocusedPositionA					#save theoretical position

			pos=autoFocusedPositionA+offset				#actual position = theoretical position + offset
			currentPos = go_to_position(pos,currentPos)	#move lense
			img = cam.start_stream_object(1000)	#grab image
			focusedPositionComplexityA=fm.fm(img,'TENENGRAD1',5,0).mean()	#calculate contrast
		elif tmp1==2:
			autoFocusedPositionB=int(round(maxZposition-goToPosition))		#calculate next position

			if autoFocusedPositionB>tmp2:				#determine moving direction, depending on direction, determine offset
				stepDir="Forward"
				offset=hysteresis
			else:
				stepDir="Backward"
				offset=-1*hysteresis
			tmp2=autoFocusedPositionB					#save theoretical position

			pos=autoFocusedPositionB+offset				#actual position = theoretical position + offset
			currentPos = go_to_position(pos,currentPos)	#move lense
			img = cam.start_stream_object(1000)	#grab image
			focusedPositionComplexityB=fm.fm(img,'TENENGRAD1',5,0).mean()	#calculate contrast

		if (abs(autoFocusedPositionA-autoFocusedPositionB)<tolerance):		#if interval is smaller than tolerance: break
			break

		if focusedPositionComplexityA>focusedPositionComplexityB: #compare 
			maxZposition=autoFocusedPositionB
			autoFocusedPositionB=autoFocusedPositionA
			focusedPositionComplexityB=focusedPositionComplexityA
			tmp1=1
		else:
			minZposition=autoFocusedPositionA
			autoFocusedPositionA=autoFocusedPositionB
			focusedPositionComplexityA=focusedPositionComplexityB
			tmp1=2	
	#depending on last step direction and maximum value, the return value must include offset to compensate hysteresis		
	if (stepDir=="Backward") and (tmp1==1):
		currentPosition = autoFocusedPositionA
		return currentPosition,focusedPositionComplexityA,fibonacciLoopCount
	elif (stepDir=="Forward") and (tmp1==2):
		currentPosition = autoFocusedPositionB
		return currentPosition,focusedPositionComplexityB,fibonacciLoopCount
	elif (stepDir=="Forward") and (tmp1==1):
		currentPosition = autoFocusedPositionB-hysteresis
		return currentPosition,focusedPositionComplexityB,fibonacciLoopCount
	elif (stepDir=="Backward") and (tmp1==2):
		currentPosition = autoFocusedPositionB+hysteresis
		return currentPosition,focusedPositionComplexityB,fibonacciLoopCount


def fibonacci(val):#uses fibonacci series
#calculates value k and index n of biggest element of fibonacci series for which k<val is true
	if val<=0:
		return 1,0
	elif val==1:
		return 2,2
	else:
		kmin1=1
		kmin2=1
		k=2
		n=2
		while k<val:
			n+=1
			kmin2=kmin1
			kmin1=k
			k=kmin1+kmin2 
		return k,n
	
def fibonacci2(nin): 
#calculates value k for biggest element of fibonacci series for which k<val is true
	if nin<=0:
		return 1
	elif nin==1:
		return 1
	else:
		kmin1=1
		kmin2=1
		k=2
		n=2
		while n<nin:
			n+=1
			kmin2=kmin1
			kmin1=k
			k=kmin1+kmin2 
		return k
		
def global_peak_single_step_debug(step,start,stop,aoi = [0,0,2544,1922]):
	# steps through complete fm curve using coarse steps
	# returns timer value for global fm maximum, fm maximum value and number of steps
	max_fm=0		#maximum fm value
	max_index=0		#timer value corresponding to maximum fm value
	index=start		#first timer value
	fm_vals=[]
	fm = ContrastMeasures()
	resetPosition(currentPosition)
	currentPos = 0
	
	#loop through timer values
	while index<=stop:
		currentPos = go_to_position(index,currentPos) #move lense to next position
		img = cam.start_stream_object(1000)	
		#grab image and calculate fm value in AOI
		fm_vals.append(fm.fm(img,'TENENGRAD1',7,0).mean())
		index+=step #calculate next timer value	
	return fm_vals
	
def global_peak_single_step(step,start,stop,aoi= [0,0,2544,1922]):
	# steps through complete fm curve using coarse steps
	# returns timer value for global fm maximum, fm maximum value and number of steps
	max_fm=0		#maximum fm value
	max_index=0		#timer value corresponding to maximum fm value
	index=start		#first timer value
	steps=0			#number of steps
	fm = ContrastMeasures()
	resetPosition(currentPosition)
	currentPos = 0
	#loop through timer values
	while index<=stop:
		currentPos = go_to_position(index,currentPos) #move lense to next position
		img = cam.start_stream_object(1000)	
		#grab image and calculate fm value in AOI
		fm_val=fm.fm(img,'TENENGRAD1',7,0).mean()
		if fm_val > max_fm:	#check if maximum occured
			max_fm=fm_val	#save maximum fm value
			max_index=index	#save timer value corresponding to maximum fm value
		steps+=1	#increase number of steps
		index+=step #calculate next timer value	
	return max_index,max_fm,steps	
	
def global_peak_two_step(c_step,f_step,start,stop,hysteresis):
# steps through complete fm curve using coarse steps
# applies fine step search around maximum
# returns timer value for global fm maximum, fm maximum value and number of steps
	#apply coarse step peak search
	cmax,cfm,csteps=global_peak_single_step(c_step,start,stop) 
	#calculate new start and stop values for fine step search
	if cmax<c_step:
		s0=0
	else:
		s0=cmax-c_step
	#apply fine step peak search	
	print(s0,cmax+c_step)
	fmax,ffm,fsteps=global_peak_single_step(f_step,s0-hysteresis,cmax+c_step-hysteresis)
	#total number of steps = number of steps for coarse search + number of steps for fine search
	steps=csteps+fsteps	
	return fmax,ffm,steps
