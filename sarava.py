# -*- coding: utf-8 -*-

"""Tools to parse prayers to northern Brazilian Quimbanda deities in the
original Portuguese and return a summary of purpose and content in English.

To be implemented: Lines, purpose (petition, thanksgiving), noble titles, tags.
"""

from unicodedata import normalize
import re

# Pontos or prayers for testing purposes

PONTO_01 = u"""
Maria Molambo,
Você não é brincadeira.
Maria Molambo,
Você mora na ladeira. (bis)
A capa encarnada,

Que eu mandei fazer,
Não é para o exú,
É pra Maria Molambê. (bis)
Olha minha gente,
Ela é farrapo só!…(bis)
È Pomba Gira Maria Molambo,
Ela é farrapo só!…(bis)

Mas que caminho tão escuro,
Que caminho tão escuro,
Que passa aquela moça,
Com sua saia de chita,
Estralando osso,
Só osso, só osso,…
Mas olha minha gente…

Quem mora na porta da lomba,
É a Pomba Gira Molambê,
Exú que mora na porta da lomba,
É Pomba Gira Molambê…
Peço licença Exú Olodê!…

Viemos coroar Pomba Gira Molambê.
"""

PONTO_02 = u"""
Não é a toa que eu tenho um trono,
Não é a toa que eu tenho uma coroa. (bis)
Eu agradeço ao Senhor das Alturas,
Eu sou Pomba Gira Rainha das Ruas.
"""

PONTO_03 = u"""
PORTÃO DE FERRRO, CADEADO DE MADEIRA 
PORTÃO DE FERRO, CADEADO DE MADEIRA 
NA PORTA DA CALUNGA QUEM MANDA É EXÚ CAVEIRA 
NA PORTA DA CALUNGA QUEM MANDA É EXÚ CAVEIRA
"""

PONTO_04 = u"""
QUEM É QUE DESCEU DO REINO, QUEM É EXU (2X)
ELE É TRANCA RUA DAS ALMAS, ELE É (2X)
"""

# Translation table for the different kingdoms or realms of experience
KINGDOMS = {
	'encruzilhada' : 'crossroads',
	'cruzeiro' : 'votary cross',
	'matas' : 'fields or weeds',
	'calunga' : 'cemetery',
	'almas' : 'souls',
	'lira' : 'harp',
	'praia' : 'beach'
}


def get_mentions(invocation, prayer):

	"""Returns slices of string after the given invocation and before the next 
	punctation mark or end of line. This has so far proven to be the simple 
	criteria with better results to identify the end of the relevant slice.
	"""

	regex = invocation + " [a-zA-Z ]+"
	mentions = re.findall(regex, prayer)
	return mentions


def get_probable_protagonist(mentions):

	"""Identifies the most likely deity from a list of slices"""

	if type(mentions) is list and len(mentions) > 0:
		return max(set(mentions), key=mentions.count)
	else:
		return None

	# TODO: Prevent spelling variants to compute as multiple entries
	# Implement smarter choice for draws

 
def get_kingdom(prayer):

	"""Returns the realm of experience with wich a deity is concerned"""

	kingdom = None
	potential_kingdoms = []

	for key, val in KINGDOMS.iteritems():
		mentions = prayer.count(key)
		if mentions > 0:
			potential_kingdoms.append((key, mentions))

	if len(potential_kingdoms) >= 1:
		most_frequent = sorted(potential_kingdoms, key=lambda x: x[1])[0]
		kingdom = KINGDOMS[most_frequent[0]]

	return kingdom

	# TODO: Write multi-kingdom variant


def get_verbose(deity):

	"""Generates a string description of the characters and places involved"""

	description = 'This prayer appears to be about '
	if 'name' in deity:
		description += deity['name'].strip()
	else:
		description += 'an unknown %s deity' % deity['gender']
	if 'kingdom' in deity:
		description += ', belonging to the kingdom of the %s' % deity['kingdom']
	description += '.'

	return description

	# TODO: Capitalize output


def extract_information(prayer):

	"""Tries to identify the deity a prayer is dedicated to, or at least the
	kingdom, or subject, it pertains to"""

	# Removes uppercase and special characters
	ponto = normalize('NFKD', prayer.lower()).encode('ASCII', 'ignore')
	deity = {}

	# First it runs a scan based on the most unambiguous potential mentions
	# Like when preceded by 'Saravá', meaning 'Hail', which is the surest one
	# Or when deities introduce themselves ('Eu Sou' or 'I am')

	sarava_mentions = get_mentions('sarava', ponto)
	eu_sou_mentions = get_mentions('eu sou', ponto)

	sarava = get_probable_protagonist([item[7:] for item in sarava_mentions])
	eu_sou = get_probable_protagonist([item[7:] for item in eu_sou_mentions])

	if sarava is not None:
		deity['name'] = sarava
	elif eu_sou is not None:
		deity['name'] = eu_sou

	else:
	# If this failed to identify a deity we proceed to a more in depth analysis.

		# We scan for mentions of male and female deities (Exus and Pomba Giras)
		mentions = get_mentions('pomba gira',ponto) + get_mentions('exu',ponto)
		probable_protagonist = get_probable_protagonist(mentions)

		if probable_protagonist is not None:
			deity['name'] = probable_protagonist

		else:
			# We at least try to see if it's about an Exu or Pomba Gira,
			# i.e. male or female, even if they are not named specifically
			gira_occurrences = ponto.count('pomba gira')
			exu_occurrences = ponto.count('exu')

			if gira_occurrences > exu_occurrences:
				deity['gender'] = 'female'
			elif gira_occurrences == exu_occurrences:
				deity['gender'] = 'neutral'
				# TODO: expand this case to count the 'she' and 'he' mentions 
				# (ela vs ele) instead
			else:
				deity['gender'] = 'male'

	# We try to identify the particular realm of relevance for a deity
	kingdom = get_kingdom(ponto)
	if kingdom is not None:
		deity['kingdom'] = kingdom

	return get_verbose(deity)


print extract_information(PONTO_01)
print extract_information(PONTO_02)
print extract_information(PONTO_03)
print extract_information(PONTO_04)
