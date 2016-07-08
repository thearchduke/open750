#!/usr/bin/env python
'''
Test suite for open750 miniblog

This work is distributed under the GPL, waivers, limitations etc.
Copyright J. Tynan Burke 2016 http://www.tynanburke.com
'''

import unittest
from models import *
from passlib.hash import sha256_crypt

class SevenFiftyTest(unittest.TestCase):
	test_user_1 = User('test user', 'test password', 'test email')
	session.add(test_user_1)
	session.commit()
	test_post_1 = SevenFifty('this is a #post #POST #Post #post', test_user_1.id)
	session.add(test_post_1)
	session.commit()

	def testPasswordHash(self, user=test_user_1):
		self.assertTrue(user.hashed_password != 'test password')
		self.assertTrue(user.verify_password('test password'))

	def testRelation(self, user=test_user_1, post=test_post_1):
		self.assertTrue(user.posts[0] == post)
		self.assertTrue(post.user == user)

	def testHashTags(self, post=test_post_1):
		self.assertTrue(len(post.hashtags) == 1)

	session.delete(test_user_1)
	session.delete(test_post_1)
	session.commit()

class SevenFiftyTest(unittest.TestCase):
	pass

class HashTagTest(unittest.TestCase):
	pass

class AFINNTest(unittest.TestCase):
	def testAnalysis(self):
		self.assertTrue(afinn.analyze_sentiment("well that went well. and good, good good, better best. enough!") == 14)
		self.assertTrue(afinn.analyze_sentiment("that was the worst goddamned opera i ever saw, it was terrible, i hated it.") == -9)
		self.assertTrue(afinn.analyze_sentiment("that. was. the. worst. goddamned. opera. i. ever. saw, it. was. terrible, i hated it.") == -9)

if __name__ == '__main__':
	unittest.main()