#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from typographus import Typographus

class TestPunctuation(unittest.TestCase):
    
    def setUp(self):
        self._typo = Typographus()
        
    def assert_typo(self, expect, input):
        try:
            self.assertEqual(expect, self.typo(input))
        except Exception, e:
            print expect.encode('utf-8')
            print self.typo(input).encode('utf-8')
            raise e
    
    def typo(self, string):
        return self._typo.process(string)
	
	def testsafeblocks(self):
	    self.assert_typo(u'<code> -->> </code>', u'<code> -->> </code>')
	
    def testmath(self):
        self.assert_typo(u'5+6&minus;7&plusmn;8', u'5+6-7+-8')
        self.assert_typo(u'===', u'============')
        self.assert_typo(u'++', u'+++++++++++')
    
    def testshortening(self):
        self.assert_typo(u'тов.&nbsp;Сталин', u'тов Сталин')
        self.assert_typo(u'1г. Воронеж', u'1г. Воронеж')
        self.assert_typo(u'стр.&nbsp;5', u'стр    5')
        self.assert_typo(u'2008&nbsp;г.', u'2008 г')
        self.assert_typo(u'25&nbsp;см', u'25  см.')
    
    def testrepeats(self):
        self.assert_typo(u'!!!', u'!!!!!!!!!!!!!!')
        self.assert_typo(u'!', u'!!')
        self.assert_typo(u'???', u'??????????')
        self.assert_typo(u'?', u'??')
    
    def testarrows(self):
        self.assert_typo(u'&rarr;', u'----->>>')
        self.assert_typo(u'&larr;', u'<<<-------')
        self.assert_typo(u'сюда&nbsp;&larr;', u'сюда <<--')
        self.assert_typo(u'туда&nbsp;&rarr;', u'туда ---->>>>>')
    
    def testmultiply(self):
        self.assert_typo(u'6&times;7', u'6x7')
    
    def testnowrap(self):
        self.assert_typo(u'<span style="white-space: nowrap;">ООО &laquo;Рога и Копыта&raquo;</span>',
                         u'ООО "Рога и Копыта"')
    
if __name__ == '__main__':
    unittest.main()