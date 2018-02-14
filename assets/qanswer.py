import json
import Levenshtein
import munkres

def compare_num(sa,ta,method,range):
	# method ->
	#	bool 	: ta +- range
	#	linear 	: ta = 100% , +- range = 0%
	
	x = float(sa)
	y = float(ta)
	
	if method == 'bool':
		if x <= (y + range) and x >= (y - range):
			return 100
	elif method == 'linear':
		if x == y:
			return 100
		elif x <= (y + range) and x >= y:
			return round_to_int( ( 1 - (x - y) / range ) * 100 )
		elif x >= (y - range) and x <= y:
			return round_to_int( ( 1 - (y - x) / range ) * 100 )
	
	return 0

def compare_str(x,y,method,range):
	# method ->
	#	all methods use Levenshtein distance to approximate error && range must be a percentage like 40%
	#	bool 	: ta +- range
	#	linear 	: ta = 100% , range = 0%
	
	if method == 'bool':
		rerr = 100 - round_to_int(Levenshtein.ratio(x, y) * 100)
		if range >= rerr:
			return 100
	elif method == 'linear':
		score = round_to_int(Levenshtein.ratio(x, y) * 100)
		if score >= range:
			return ((score - range) * 100) / range
	
	return 0

def round_to_int(fl):
	res = fl - int(fl)
	if res >= 0.5:
		return int(fl) + 1
	else:
		return int(fl)

def to_number(x):
	result = None
	
	# python treats bools like numbers and will cast False -> 0, True -> 1, so get rid of this case first
	if type(x) is bool:
		return None
	
	# if we already have number, great, just return it
	if type(x) is int or type(x) is float or type(x) is long or type(x) is complex:
		return x
	
	# try to cast a string or unicode to different numeric types, if any succeed, return it
	if type(x) is str or type(x) is unicode:
		try:
			result = int(x)
			return result
		except:
			pass
		
		try:
			result = long(x)
			return result
		except:
			pass
		
		try:
			result = float(x)
			return result
		except:
			pass
		
		try:
			result = complex(x)
			return result
		except:
			pass
			
	# if it's any other type, assume it's not numeric
	return None

def grade(subblock,submittedans):
	# QUESTION LOOP - loop through each question that requires an answer
	# SUBMISSION LOOP - loop through each answer submitted by student
	# ANSWER LOOP - loop through all valid answers to the question
	
	finalscore = 0
	allanswers = ''
	# QUESTION LOOP
	for key in subblock:
		sanswers = submittedans[key]
		
		allanswers += str(sanswers) + ","
		
		correct = 0
		answerMatrix = [0] * len(sanswers)
		
		sindex = 0
		# SUBMISSION LOOP
		for sanswer in sanswers:
			# get student answer as number or string
			sna = to_number(sanswer)
			sa = sna if sna else sanswer
			
			tindex = 0
			answerMatrix[sindex] = [0] * len(subblock[key]['values'])
			# ANSWER LOOP
			for tanswer in subblock[key]['values']:
				# get author answer as number or string
				tna = to_number(tanswer)
				ta = tna if tna else tanswer
				
				# handle numeric grading
				if tna is not None:
					ta = tna
					grade = compare_num(sa,ta,subblock[key]['grading'],subblock[key]['margin'])
					if grade:
						correct += 1
						answerMatrix[sindex][tindex] = grade
				# handle string grading
				else:
					ta = tanswer
					grade = compare_str(sa,ta,subblock[key]['grading'],subblock[key]['margin'])
					if grade:
						correct += 1
						answerMatrix[sindex][tindex] = grade
				
				tindex += 1
			sindex += 1
		
		# multiply entire matrix by -1 to use as reverse hungarian algorithm
		for row in range(len(answerMatrix)):
			for column in range(len(answerMatrix)):
				answerMatrix[row][column] *= -1 
		
		# compute hungarian algorithm
		m = munkres.Munkres()
		indexes = m.compute(answerMatrix)
		
		# accumulate total score & multiple by -1 to reverse it back
		score = 0
		for row, column in indexes:
			value = answerMatrix[row][column]
			score += value
		
		score *= -1
		
		# total score for this particular question
		total = 100 * int(subblock[key]['match'])
		
		# add how much this particular question is worth for the whole result
		finalscore += min(round_to_int((float(score) / float(total)) * 100),total) *  int(subblock[key]['percentage'])# convert to percentage like 50%
			
	adjustedscore = round( (float(finalscore) / float(10000)) , 2 ) # this changes it to a 1 point scale & rounds to 2 decimal points
	
	return adjustedscore


