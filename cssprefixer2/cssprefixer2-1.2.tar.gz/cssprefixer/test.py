import unittest
import cssprefix

class GetCssData(unittest.TestCase):
    def test_getRules(self):
        css = 'body{background: #FFF;font-family:FontAwesome;}'
        self.assertEqual(cssprefix.getStyles(css), [dict(
            name='body',
            rules=[
                ['background','#FFF'],
                ['font-family','FontAwesome']
            ]
        )])
    
    def test_removeComments(self):
        css = 'body{background:#fff;}/*testing*/a{color:#fff;}'
        self.assertEquals(cssprefix.getStyles(css), [{
            'name':'body',
            'rules':[
                ['background','#fff']
            ]
        },
        {
            'name':'a',
            'rules':[
                ['color', '#fff']
            ]
        }])
    

    def test_getMedia(self):
        css = '@media screen{a{color:#fff;}}'

        self.assertEquals(cssprefix.getStyles(css), [{
            'name':'@media screen',
            'wrapper':[{
                'name':'a',
                'rules':[
                    ['color', '#fff']
                ]
            }]
        }])

    def test_getRulesMultiple(self):
        css = 'body{background: #FFF;font-family:FontAwesome;}a{color:inherit;font-size:inherit;}'
        self.assertEqual(cssprefix.getStyles(css), [dict(
            name='body',
            rules=[
                ['background','#FFF'],
                ['font-family','FontAwesome']
            ]
        ), dict(
            name='a',
            rules=[
                ['color','inherit'],
                ['font-size','inherit']
            ]
        )])

    def test_getRulesSelector(self):
        css = 'body{background: #FFF;font-family:FontAwesome;}a:hover{text-decoration:underline;}'
        self.assertEqual(cssprefix.getStyles(css), [dict(
            name='body',
            rules=[
                ['background','#FFF'],
                ['font-family','FontAwesome']
            ]
        ), dict(
            name='a:hover',
            rules=[
                ['text-decoration','underline']
            ]
        )])

    def test_getRulesUrl(self):
        css = 'body{background-image:url("http://www.google.com");}'
        self.assertEquals(cssprefix.getStyles(css), [dict(
            name='body',
            rules=[
                ['background-image','url("http://www.google.com")']
            ]
        )])

class GenCssText(unittest.TestCase):
    def setUp(self):
        self.css = [dict(
            name='body',
            rules=[
                ['background','#FFF'],
                ['font-family','FontAwesome']
            ]
        ), dict(
            name='a:hover',
            rules=[
                ['text-decoration','underline']
            ]
        )]

    def test_genText(self):
        text ="""body{
    background: #FFF;
    font-family: FontAwesome;
}

a:hover{
    text-decoration: underline;
}"""
        self.assertEquals(cssprefix.generateText(self.css), text)

    def test_genTextMinify(self):
        text = 'body{background:#FFF;font-family:FontAwesome;}a:hover{text-decoration:underline;}'
        self.assertEquals(cssprefix.generateText(self.css, True), text)

    def test_genMedia(self):
        css = [{'name':'a', 'rules':[['color','#000']]},{'name':'@media screen', 'wrapper':[{'name':'strong', 'rules':[['font-weight','bold']]}]}]
        text = 'a{color:#000;}@media screen{strong{font-weight:bold;}}'
        self.assertEquals(cssprefix.generateText(css, True), text)

class RuleTester(unittest.TestCase):
    def setUp(self):
        self.rules = __import__('rules')

class RuleCssText(RuleTester):
    def test_nothing(self):
        orig = ['color','#FFF']
        self.assertEquals(self.rules.process(orig), [orig])

    def test_replaceBase(self):
        orig = ['border-radius','50%']
        result = [
            ['-moz-border-radius','50%'],
            ['-webkit-border-radius','50%'],
            ['border-radius','50%']
        ]
        self.assertEquals(self.rules.process(orig), result)

    def test_displayNormal(self):
        orig = ['display', 'none']
        self.assertEquals(self.rules.process(orig), [orig])

class RuleCssFlexbox(RuleTester):
    def test_flexbox(self):
        orig = ['display', 'flex']
        result = map(lambda x:['display',x], [
            '-webkit-box', '-moz-box',
            '-ms-flexbox', '-webkit-flex', 'flex'
        ])
        self.assertEquals(self.rules.process(orig), result)
    
    def test_flexbox_flex(self):
        orig = ['flex', '1']
        result = map(lambda x:[x,'1'], [
            '-webkit-box-flex', '-moz-box-flex',
            '-ms-flex', '-webkit-flex', 'flex'
        ])
        self.assertEquals(self.rules.process(orig), result)

    def test_flexbox_flexbasis(self):
        orig = ['flex', '0 0 500px']
        result = [['width', '500px']] + map(lambda x:[x,'0 0 500px'], [
            '-webkit-box-flex', '-moz-box-flex',
            '-ms-flex', '-webkit-flex', 'flex'
        ])
        self.assertEquals(self.rules.process(orig), result)

    def test_flexbox_order(self):
        orig = ['order', '2']
        result = map(lambda x:[x,'2'], [
            '-webkit-box-ordinal-group', '-moz-box-ordinal-group',
            '-ms-flex-order', '-webkit-flex-order', 'order'
        ])
        self.assertEquals(self.rules.process(orig), result)
    
    def test_flexbox_items(self):
        orig = ['align-items', 'flex-start']
        result = map(lambda x:[x, 'start'], '-moz-box-align -webkit-box-align -ms-flex-align'.split(' '))
        result += map(lambda x:[x, 'flex-start'], '-webkit-align-items align-items'.split(' '))
        self.assertEquals(self.rules.process(orig), result)

    def test_flexbox_item(self):
        orig = ['align-self', 'flex-start']
        result = map(lambda x:[x, 'start'], '-moz-box-item-align -webkit-box-item-align -ms-flex-item-align'.split(' '))
        result += map(lambda x:[x, 'flex-start'], '-webkit-align-self align-self'.split(' '))
        self.assertEquals(self.rules.process(orig), result)

    def test_flexbox_content(self):
        orig = ['align-content', 'space-around']
        result = [['-ms-flex-line-pack', 'distribute']]
        result += map(lambda x:[x, 'space-around'], '-webkit-align-content align-content'.split(' '))
        self.assertEquals(self.rules.process(orig), result)

    def test_flexbox_justify(self):
        orig = ['justify-content', 'space-around']
        result = map(lambda x:[x, 'justify'], '-moz-box-pack -webkit-box-pack'.split(' '))
        result += [['-ms-flex-pack', 'distribute']]
        result += map(lambda x:[x, 'space-around'], '-webkit-justify-content justify-content'.split(' '))
        self.assertEquals(self.rules.process(orig), result)

    ### TODO: flex-direction flex-flow flex-wrap
    def test_flexbox_direction1(self):
        orig = ['flex-direction', 'row']
        result =  map(lambda x:[x, 'normal'], '-moz-box-direction -webkit-box-direction'.split(' '))
        result += map(lambda x:[x, 'horizontal'], '-moz-box-orient -webkit-box-orient'.split(' '))
        result += map(lambda x:[x, 'row'], '-ms-flex-direction -webkit-flex-direction flex-direction'.split(' '))
        self.assertEquals(self.rules.process(orig), result)
    
    def test_flexbox_direction2(self):
        orig = ['flex-direction', 'row-reverse']
        result =  map(lambda x:[x, 'reverse'], '-moz-box-direction -webkit-box-direction'.split(' '))
        result += map(lambda x:[x, 'horizontal'], '-moz-box-orient -webkit-box-orient'.split(' '))
        result += map(lambda x:[x, 'row-reverse'], '-ms-flex-direction -webkit-flex-direction flex-direction'.split(' '))
        self.assertEquals(self.rules.process(orig), result)

    def test_flexbox_direction3(self):
        orig = ['flex-direction', 'column']
        result =  map(lambda x:[x, 'normal'], '-moz-box-direction -webkit-box-direction'.split(' '))
        result += map(lambda x:[x, 'vertical'], '-moz-box-orient -webkit-box-orient'.split(' '))
        result += map(lambda x:[x, 'column'], '-ms-flex-direction -webkit-flex-direction flex-direction'.split(' '))
        self.assertEquals(self.rules.process(orig), result)

    def test_flexbox_direction4(self):
        orig = ['flex-direction', 'column-reverse']
        result =  map(lambda x:[x, 'reverse'], '-moz-box-direction -webkit-box-direction'.split(' '))
        result += map(lambda x:[x, 'vertical'], '-moz-box-orient -webkit-box-orient'.split(' '))
        result += map(lambda x:[x, 'column-reverse'], '-ms-flex-direction -webkit-flex-direction flex-direction'.split(' '))
        self.assertEquals(self.rules.process(orig), result)

    def test_flexbox_direction_error(self):
        orig = ['flex-direction', 'something']
        with self.assertRaises(ValueError):
            self.rules.process(orig)

    def test_flexbox_wrap(self):
        orig = ['flex-wrap', 'wrap']
        result = map(lambda x:[x, 'wrap'], '-ms-flex-wrap -webkit-flex-wrap flex-wrap'.split(' '))
        self.assertEquals(self.rules.process(orig), result)
    
    def test_flebox_flow(self):
        orig = ['flex-flow', 'column']
        result =  map(lambda x:[x, 'normal'], '-moz-box-direction -webkit-box-direction'.split(' '))
        result += map(lambda x:[x, 'vertical'], '-moz-box-orient -webkit-box-orient'.split(' '))
        result += map(lambda x:[x, 'column'], '-ms-flex-direction -webkit-flex-direction flex-direction'.split(' '))

        self.assertEquals(self.rules.process(orig), result)

    def test_flebox_flow_full(self):
        orig = ['flex-flow', 'column wrap']
        result =  map(lambda x:[x, 'normal'], '-moz-box-direction -webkit-box-direction'.split(' '))
        result += map(lambda x:[x, 'vertical'], '-moz-box-orient -webkit-box-orient'.split(' '))
        result += map(lambda x:[x, 'column'], '-ms-flex-direction -webkit-flex-direction flex-direction'.split(' '))
        result += map(lambda x:[x, 'wrap'], '-ms-flex-wrap -webkit-flex-wrap flex-wrap'.split(' '))

        self.assertEquals(self.rules.process(orig), result)

class GradientTest(RuleTester):
    def test_linear(self):
        orig = '.div{background:linear-gradient(to right, #fff, #000);}'
        result = '.div{background:-moz-linear-gradient(left,#fff,#000);background:-webkit-linear-gradient(left,#fff,#000);background:linear-gradient(to right,#fff,#000);}'
        self.assertEquals(cssprefix.process(orig, True), result)

    def test_nothing(self):
        orig = '.div{background:#fff;}'
        self.assertEquals(cssprefix.process(orig, True), orig)

class FullCssTest(unittest.TestCase):
    def test_flexbox(self):
        orig = 'div{display:flex;margin:4rem 0;}div a{color:inherit;}'
        result = 'div{display:-webkit-box;display:-moz-box;display:-ms-flexbox;display:-webkit-flex;display:flex;margin:4rem 0;}div a{color:inherit;}'
        self.assertEquals(cssprefix.process(orig, True), result)

    def test_media(self):
        orig = 'a{color:#fff;}@media screen{a{color:#000;}}'
        self.assertEquals(cssprefix.process(orig, True), orig)

class TextAlignTest(RuleTester):
    def test_normal(self):
        orig = ['text-align', 'left']
        self.assertEquals(self.rules.process(orig), [orig])
    
    def test_center(self):
        orig = ['text-align', 'center']
        result = [orig] + map(lambda x:['text-align', x+'-center'], ['-moz', '-webkit'])
        self.assertEquals(self.rules.process(orig), result)

if __name__=='__main__':
    unittest.main()
