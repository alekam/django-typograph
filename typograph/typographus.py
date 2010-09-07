# -*- coding: utf-8 -*-

import re, htmlentitydefs, unicodedata

__all__ = ('Typographus', 'typo')

def entity(name):
    return unichr(htmlentitydefs.name2codepoint[name])


sym = {
    'nbsp':     entity('nbsp'),
    'lquote':   entity('laquo'),
    'rquote':   entity('raquo'),
    'mdash':    entity('mdash'),
    'ndash':    entity('ndash'),
    'minus':    entity('minus'),
    'hellip':   entity('hellip'),
    'copy':     entity('copy'),
    'trade':    entity('trade'),
    'apos':     "'",
    'reg':      entity('reg'),
    'multiply': entity('times'),
    '1/2':      entity('frac12'),
    '1/4':      entity('frac14'),
    '3/4':      entity('frac34'),
    'plusmn':   entity('plusmn'),
    'rarr':     entity('rarr'),
    'larr':     entity('larr'),
    'rsquo':    entity('rsquo'),
    'rsaquo':   entity('rsaquo'),
    'lsaquo':   entity('lsaquo'),
    ':)':       ':)',
    }

safeBlocks = {
    '<pre[^>]*>':    '<\/pre>',
    '<style[^>]*>':  '<\/style>',
    '<script[^>]*>': '<\/script>',
    '<!--':          '-->',
    '<code[^>]*>':   '<\/code>',
    }

space = '[\s|%s]' % sym['nbsp']

html_tag = u''
hellip = u'\.{3,}'

#Слово
word = u'[a-zA-Zа-яА-Я_]'
phrase_begin = ur"(?:%s|%s|\d|\n)" % (hellip, word)

#Конец слова
phrase_end = ur"(?:%s|%s|\n)" % (hellip, word)

#Знаки препинания (троеточие и точка - отдельный случай!)
punctuation = u'[?!:,;]'

all_punctuation = u'[?!:,;\.%s]' % entity('hellip')

#Аббревиатуры
abbr = ur'(?:ООО|ОАО|ЗАО|ЧП|ИП|НПФ|НИИ)'

#Предлоги и союзы
prepos = u'а|в|во|вне|и|или|к|о|с|у|о|со|об|обо|от|ото|то|на|не|ни|но|из|изо|за|уж|на|по|под' \
    + u'|подо|пред|предо|про|над|надо|как|без|безо|что|да|для|до|там|ещё|их|или|ко|меж|между' \
    + u'|перед|передо|около|через|сквозь|для|при|я'

metrics = u'мм|см|м|км|кг|б|кб|мб|гб|dpi|px' # с граммами сложнее - либо граммы либо города

shortages = u'гн|гжа|гр|г|тов|пос|c|ул|д|пер|м'

money = u'руб\.|долл\.|евро|у\.е\.'
counts = u'млн\.|тыс\.'

# any_quote = u'(?:%s|%s|%s|%s|&quot;|")' % (sym['lquote'], sym['rquote'], sym['lquote2'], sym['rquote2'])



# fuck unicode specs
known_single_quotes = ( 'apostrophe',
                        'grave accent',
                        'grave accent',
                        'left single quotation mark',
                        'right single quotation mark',
                        'modifier letter prime',
                        'modifier letter grave accent',
                        'modifier letter acute accent',
                        'modifier letter vertical line',
                        'modifier letter turned comma',
                        'modifier letter apostrophe',
                        'modifier letter reversed comma',
                        'armenian apostrophe',
                        'greek tonos' )

any_single_quote = u'(?:%s)' % ('|'.join(map(unicodedata.lookup, known_single_quotes)))


known_quotes = ( 'quotation mark', 
                 'left double quotation mark',
                 'right double quotation mark',
                 'modifier letter double prime',
                 'double acute accent',
                 'left-pointing double angle quotation mark',
                 'right-pointing double angle quotation mark' )

any_quote = u'(?:%s)' % ('|'.join(map(unicodedata.lookup, known_quotes)))


brace_open = ur'(?:\(|\[|\{)'
brace_close = ur'(?:\)|\]|\})'

arrow_left = '[<|%s]' % sym['lsaquo']
arrow_right = '[>|%s]' % sym['rsaquo']

def nowrap(string):
    #return string
    return re.sub(r'\s', sym['nbsp'], string)


class Rule:

    def __init__(self, pattern, replacement, flag=re.X):
        self.pattern = pattern
        self.replacement = replacement
        self.flag = flag
        self.regexp = re.compile(pattern, flag)

    def __call__(self, data):
        return self.regexp.sub(self.replacement, data)

    def __repr__(self):
        return (u"re.compile('%s', %s).sub('%s')" % (self.pattern, self.flag, self.replacement)).encode('utf-8')

    def __str__(self):
        return self.__repr__()

def compile_ruleset(*ruleset):
    """ compiles rulesset into list of callables """
    result = []
    for rule_desc in ruleset:
        flag = re.X
        if type(rule_desc) in [tuple, list]:
            pattern, replacement = rule_desc[:2]
            if len(rule_desc) > 2:
                flag = rule_desc[2]
        elif type(rule_desc) is dict:
            pattern = rule_desc['pat']
            replacement = rule_desc['rep']
            if 'mod' in rule_desc:
                flag = rule_desc['mod']
        else:
            raise Exception, 'unknown rule: %s' % repr(rule_desc)
        result.append(Rule(pattern, replacement, flag))
    return result


rules_strict = compile_ruleset(
    
    # много пробелов или табуляций -> один пробел
    (r'%s+' % space, u' '),
    
    # запятые после "а" и "но"
    (ur'(?<=[^,])(?=\s(?:а|но)\s)', ur','),
    
    )


rules_symbols = compile_ruleset(
    
    # пробелы между знаками препинания - нафик не нужны
    (r'(?<=%s)%s+(?=%s)' % (all_punctuation, space, all_punctuation), ''),
    
    (r'!{3,}', '!!!'), # больше 3 заменяем на 3
    (r'(?<!!)!!(?!!)', '!'), # 2 меняем на 1
    
    (r'\?{3,}', '???'), # аналогично
    (r'(?<!\?)\?\?(?!\?)', '?'),
    
    (r';+', r';'), # эти знаки строго по одному
    (r':+', r':'),
    (r',+', r','),
    
    (r'\+\++', '++'),
    (r'--+', '--'),
    (r'===+', '==='),
    
    # убиваем эмобредни
    (r'!+\?+[!|\?]*', '?!'),
    (r'\?+!+[!|\?]*', '?!'),

    # знаки (c), (r), (tm)
    (ur'\([cс]\)', sym['copy'], re.I), # русский и латинский варианты
    (ur'\(r\)', sym['reg'], re.I),
    (ur'\(tm\)', sym['trade'], re.I),
    
    (r'\s+(?=[%s|%s|%s])' % (sym['trade'], sym['copy'], sym['reg']), ''),
    
    # автор неправ. скорее всего малолетки балуются
    (ur'\.{2,}', sym['hellip']),
    
    # спецсимволы для 1/2 1/4 3/4
    (ur'\b1/2\b', sym['1/2']),
    (ur'\b1/4\b', sym['1/4']),
    (ur'\b3/4\b', sym['3/4']),
    
    # какая-то муть с апострофами
    # (ur"(?<=%s)'(?=%s)" % (word, word), sym['rsquo']),
    # (ur"'", sym['apos']),
    (any_single_quote, sym['rsquo']),
    
    
    # размеры 10x10, правильный знак + убираем лишние пробелы
    (ur'(?<=\d)\s*[x|X|х|Х]\s*(?=\d)', sym['multiply']),
    
    # +-
    (r'\+-', sym['plusmn']),
    
    (r'(?<=\S)\s+(?=-+%s+|%s+-+)' % (arrow_right, arrow_left), sym['nbsp']), # неразрывные пробелы перед стрелками
    (r'(-+%s+|%s+-+)\s+(?=\S)' % (arrow_right, arrow_left), r'\1' + sym['nbsp']), # неразрывные пробелы после стрелок
    
    # стрелки
    (r'<+-+', sym['larr']),
    (r'-+>+', sym['rarr']),
    
    )

rules_quotes = compile_ruleset(
    
    # разносим неправильные кавычки
    #(ur'([^"]\w+)"(\w+)"', u'\g<1> "\g<2>"'),
    (ur'([^"]\S+)"(\S+)"', ur'\1 "\2"'),
    (ur'"(\S+)"(\S+)', ur'"\1" \2'),
    
    # превращаем кавычки в ёлочки. Двойные кавычки склеиваем.
    # ((?:«|»|„|“|&quot;|"))((?:\.{3,5}|[a-zA-Zа-яА-Я_]|\n))
    (u"(%s)(%s)" % (any_quote, phrase_begin), u'%s\g<2>' % sym['lquote']),
    
    # ((?:(?:\.{3,5}|[a-zA-Zа-яА-Я_])|[0-9]+))((?:«|»|„|“|&quot;|"))
    (ur"((?:%s|(?:[0-9]+)))(%s)" % (phrase_end, any_quote), u'\g<1>%s' % sym['rquote']),
    
    (sym['rquote'] + any_quote, sym['rquote']+sym['rquote']),
    (any_quote + sym['lquote'], sym['lquote']+sym['lquote']),
    
    )

rules_braces = compile_ruleset(
    
    # оторвать скобку от слова
    (ur'(?<=\S)(?=%s)' % brace_open, ' '),
    (ur'(?<=%s)(?=\S)' % brace_close, ' '),
    
    # слепляем скобки со словами
    (ur'(?<=%s)\s' % brace_open, ''),
    (ur'\s(?=%s)' % brace_close, ''),
    
    # между закрывающей скобкой и знаком препинания не нужен пробел
    (r'(?<=%s)%s(?=%s)' % (brace_close, space, all_punctuation), ''),
    
    )

rules_main = compile_ruleset(
    
    # нахер пробелы перед знаками препинания
    (r'\s+(?=[\.,:;!\?])', ''),
    
    # а вот после - очень даже кстати
    (r'(?<=[\.,:;!\?])(?![\.,:;!\?\s])', ' '),
    
    # знак дефиса, ограниченный с обоих сторон цифрами — на минус.
    (r'(?<=\d)-(?=\d)', sym['minus']),
    
    # оторвать тире от слова
    (r'(?<=\w)-\s+', ' - '),
    
    # неразрывные названия организаций и абревиатуры форм собственности
    (ur'(%s)\s+"([^"]+)"' % abbr, nowrap(ur'\1 "\2"')),
    
    # нельзя отрывать сокращение от относящегося к нему слова.
    # например: тов. Сталин, г. Воронеж
    # ставит пробел, если его нет. и точку тоже ставит на всякий случай ??????. :)  
    (ur'([^\w][%s])(\.?)\s*(?=[А-Я\d])' % shortages, r'\1\2%s' % sym['nbsp']),
    
    # не отделять стр., с. и т.д. от номера.
    (ur'([^\w][стр|табл|рис|илл])\.?\s*(?=\d+)', r'\1.%s' % sym['nbsp'], re.S | re.I),
    
    # не разделять 2007 г., ставить пробел, если его нет. Ставит точку, если её нет. <- это бред
    # {"pat": u'([0-9]+)\s*([гГ])\.\s', "rep": u'\g<1>%s\g<2>. ' % sym['nbsp'], "mod": re.S},
    (ur'(?<=\d{4,4})\.?\s?(гг?)\.?([^\w]?)', r'%s\1.\2' % sym['nbsp']),
    
    # неразрывный пробел между цифрой и единицей измерения <- и это бред тоже
    # {"pat": u'([0-9]+)\s*(%s)' % metrics, "rep": u'\g<1>%s\g<2>' % sym['nbsp'], "mod": re.S},
    (ur'(\d+)\s*(%s)\.?' % metrics, r'\1%s\2' % sym['nbsp'], re.S),
    
    # Сантиметр в квадрате
    # (u'(\s%s)(\d+)' % metr=ics, u'\g<1><sup>\g<2></sup>'),
    
    # Знак дефиса или два знака дефиса подряд — на знак длинного тире. 
    # + Нельзя разрывать строку перед тире, например: Знание — сила, Курить — здоровью вредить.
    (u'(\s+)(--?|—|%s)(?=\s)' % sym['mdash'], sym['nbsp'] + sym['mdash']),
    (u'(^)(--?|—|%s)(?=\s)' % sym['mdash'], sym['mdash']),
    
    # Нельзя оставлять в конце строки предлоги и союзы - убира слеш с i @todo переработать регулярку
    #{"pat": u'(?<=\s|^|\W)(%s)(\s+)' % prepos, "rep": u'\g<1>'+sym['nbsp'], "mod": re.I},
    
    # Нельзя отрывать частицы бы, ли, же от предшествующего слова, например: как бы, вряд ли, так же.
    # {"pat": u"(?<=\S)(\s+)(ж|бы|б|же|ли|ль|либо|или)(?=[\s)!?.])", "rep": sym['nbsp'] + u'\g<2>'},
    (ur'(?<=\S)\s+(ж|бы|б|же|ли|ль|либо|или)(?!\w)', sym['nbsp'] + r'\1'),
    
    # # Неразрывный пробел после инициалов.
    (u'([А-ЯA-Z]\.)\s?([А-ЯA-Z]\.)\s?([А-Яа-яA-Za-z]+)', u'\g<1>\g<2>%s\g<3>' % sym['nbsp'], re.S),
    
    # Сокращения сумм не отделяются от чисел.         
    (u'(\d+)\s?(%s)' % counts, u'\g<1>%s\g<2>' % sym['nbsp'], re.S),
    
    #«уе» в денежных суммах
    (u'(\d+|%s)\s?уеs' % counts, u'\g<1>%sу.е.' % sym['nbsp']),
    
    # Денежные суммы, расставляя пробелы в нужных местах.
    (u'(\d+|%s)\s?(%s)' %(counts, money), u'\g<1>%s\g<2>' % sym['nbsp'], re.S),
    
    # Номер версии программы пишем неразрывно с буковкой v.
    (u'([vв]\.) ?([0-9])', u'\g<1>%s\g<2>' % sym['nbsp'], re.I),
    (u'(\w) ([vв]\.)', u'\g<1>%s\g<2>' % sym['nbsp'], re.I),
    
    
    # % не отделяется от числа
    # {"pat": u'([0-9]+)\s+%', "rep": u'\g<1>%'}
    (r'(?<=\d)\s+(?=%)', ''),
    
    )


rules_smiles = compile_ruleset(
    
    (r'[:|;|-]*?\){3,}', sym[':)']),
    
)


final_cleanup = compile_ruleset(
    
    (r'\s(?=%s)' % all_punctuation, ''),
    
)

class Typographus:
    
    encoding = None
    
    def __init__(self, encoding = None):
        self.encoding = encoding
        
    def addSafeBlock(self, openTag, closeTag):
        safeBlocks[openTag] = closeTag
        
    def getSafeBlockPattern(self):
        pattern = u'(';
        for key, value in safeBlocks.items():
            pattern += u"%s.*%s|" % (key, value)
            
        pattern+= u'<[^>]*[\s][^>]*>)';
        return pattern
    
    
    def removeRedundantBlocks(self, string):
        blocks = {}
        def replace(m):
            value = m.group()
            if(len(value)==3):
                return value
            
            key = u'<%s>' % (len(blocks))
            blocks[key] = value
            return key
        
        pattern = self.getSafeBlockPattern() 
        
        string = re.compile(pattern, re.U|re.S|re.I).sub(replace, string)
        
        string = re.compile(ur"</?.*?/?>", re.U|re.S|re.I).sub(replace, string)
        
        return {"replaced": string, "blocks": blocks}
    
    def return_blocks_to_string(self, string, blocks):
        for key, value in blocks.items():
            string = string.replace(key, value)
        return string
    
    def process(self, string):
        
        if not isinstance(string, unicode):
            raise Exception, u'only unicode instances allowed for Typographus'
        
        
        value = self.removeRedundantBlocks(string)
        
        string = value["replaced"]
        blocks = value["blocks"]
        
        string = self.typo_text(string)
        
        string = self.return_blocks_to_string(string, blocks)
        return string
    
    def typo_text(self, string):
        
        if (string.strip() == ''):
            return ''
        
        for rule_set in (rules_strict, rules_main, rules_symbols, rules_braces,
                         rules_quotes, rules_smiles, final_cleanup):
            string = reduce(lambda string, rule: rule(string), rule_set, string)
        
        # вложенные кавычки
        #         i = 0
        #         lev = 5
        
#         matchLeftQuotes = re.compile(u'«(?:[^»]*?)«')#мачит две соседние левые елочки
#         matchRightQuotes = re.compile(u'»(?:[^«]*?)»')
        
#         replaceOuterQuotes = re.compile(u'«([^»]*?)«(.*?)»')
#         replaceRightQuotes = re.compile(u'»([^«]*?)»')
#         while  i<5 and matchLeftQuotes.match(string):
#             i+=1
#             rep = u'%s\g<1>%s\g<2>%s' % (q['lq'], sym['lquote2'], sym['rquote2'])
#             string = replaceOuterQuotes.sub(rep, string)
#             i+=1
#             while i<lev and matchRightQuotes.match(string):
#                 i+=1
#                 string = replaceRightQuotes.sub(sym['rquote2'] + u'\g<1>%s' % q['rq'], string);
        
#         string = string.replace(u'<nowrap>', sym['lnowrap']).replace(u'</nowrap>', sym['rnowrap'])
        
        return string.strip()

def typo(string):
    return Typographus().process(string)
