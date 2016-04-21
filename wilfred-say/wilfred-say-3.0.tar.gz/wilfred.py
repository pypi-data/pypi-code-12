from __future__ import unicode_literals, print_function

import random
import textwrap


"""wilfred-say: prints Wilfred quotes to the commandline"""


__verison__ = '3.0.0'


QUOTES = [{
    'text': 'Sanity and happiness are an impossible combination.',
    'author': 'Mark Twain',
    'season': 1,
    'episode': 1
}, {
    'text': 'Trust thyself only, and another shall not betray thee.',
    'author': 'Thomas Fuller',
    'season': 1,
    'episode': 2
}, {
    'text': 'Fear has its uses but cowardice has none.',
    'author': 'Mahatma Ghandi',
    'season': 1,
    'episode': 3
}, {
    'text': 'Happiness can exist only in acceptance.',
    'author': 'George Orwell',
    'season': 1,
    'episode': 4
}, {
    'text': 'Seek respect mainly from thyself, for it comes first from within.',
    'author': 'Steven H. Coogler',
    'season': 1,
    'episode': 5
}, {
    'text': 'Conscience is the dog that can\'t bite, but never stops barking.',
    'author': 'Proverb',
    'season': 1,
    'episode': 6
}, {
    'text': 'In general, pride is at the bottom of all great mistakes.',
    'author': 'Steven H. Coogler',
    'season': 1,
    'episode': 7
}, {
    'text': 'Anger as soon as fed is dead -- tis starving makes it fat.',
    'author': 'Emily Dickinson',
    'season': 1,
    'episode': 8
}, {
    'text': 'Make no judgements where you have no compassion.',
    'author': 'Anne McCaffrey',
    'season': 1,
    'episode': 9
}, {
    'text': 'Isolation is a self-defeating dream.',
    'author': 'Carlos Salinas de Gortari',
    'season': 1,
    'episode': 10
}, {
    'text': 'Doubt must be no more than vigilance, otherwise it can become dangerous.',
    'author': 'George C. Lichtenberg',
    'season': 1,
    'episode': 11
}, {
    'text': 'Love is a willingless to sacrifice.',
    'author': 'Michael Novak',
    'season': 1,
    'episode': 12
}, {
    'text': 'The value of identity is that so often with it comes purpose.',
    'author': 'Richard R. Grant',
    'season': 1,
    'episode': 13
},{
    'text': 'Discontent is the first necessity of progress.',
    'author': 'Thomas Edison',
    'season': 2,
    'episode': 1
}, {
    'text': 'Some of us think holding on makes us strong, but sometimes it is letting go.',
    'author': 'Herman Hesse',
    'season': 2,
    'episode': 2
}, {
    'text': 'Let not a man guard his dignity but let his dignity guard him.',
    'author': 'Ralph Waldo Emerson',
    'season': 2,
    'episode': 3
}, {
    'text': 'Guilt: the gift that keeps on giving.',
    'author': 'Erma Bombeck',
    'season': 2,
    'episode': 4
}, {
    'text': 'Be here now.',
    'author': 'Ram Dass',
    'season': 2,
    'episode': 5
}, {
    'text': 'The master understands that the universe is forever out of control.',
    'author': 'Lao Tzu',
    'season': 2,
    'episode': 6
}, {
    'text': 'Our biggest problems arise from the avoidance of smaller ones.',
    'author': 'Jeremy Caulfield',
    'season': 2,
    'episode': 7
}, {
    'text': 'The truth will set you free, but first it will make you miserable',
    'author': 'James A. Garfield',
    'season': 2,
    'episode': 8
}, {
    'text': 'The thing that lies at the foundation of positive change is service to a fellow human being',
    'author': 'Lee Iacocca',
    'season': 2,
    'episode': 9
}, {
    'text': 'Honesty and transparency make you vulnerable. Be honest and transparent anyway',
    'author': 'Mother Teresa',
    'season': 2,
    'episode': 10
}, {
    'text': 'If you do not ask the right questions, you do not get the right answers.',
    'author': 'Edward Hodnett',
    'season': 2,
    'episode': 11
}, {
    'text': 'Resentment is like taking poison and waiting for the other person to die.',
    'author': 'Malachy McCourt',
    'season': 2,
    'episode': 12
}, {
    'text': 'If we knew each other\'s  secrets, what comfort should we find.',
    'author': 'John Churton Collins',
    'season': 2,
    'episode': 13
},{
    'text': 'The mistake is thinking that there can be an antidote to the uncertainty.',
    'author': 'David Levithan',
    'season': 3,
    'episode': 1
}, {
    'text': 'Cure sometimes, treat often, comfort always.',
    'author': 'Hippocrates',
    'season': 3,
    'episode': 2
}, {
    'text': 'Suspicion is a heavy armor and with its weight it impedes more than it protects.',
    'author': 'Robert Burns',
    'season': 3,
    'episode': 3
}, {
    'text': 'Sincerity, even if it speaks with a stutter, will sound eloquent when inspired.',
    'author': 'Eiji Yoshikawa',
    'season': 3,
    'episode': 4
}, {
    'text': 'I have little shame, no dignity - all in the name of a better cause.',
    'author': 'A.J. Jacobs',
    'season': 3,
    'episode': 5
}, {
    'text': 'Truth may sometimes hurt, but delusion harms.',
    'author': 'Vanna Bonta',
    'season': 3,
    'episode': 6
}, {
    'text': 'Intuition is more important to discovery than logic.',
    'author': 'Henri Poincare',
    'season': 3,
    'episode': 7
}, {
    'text': 'How weird was it to drive streets I knew so well. What a different perspective.',
    'author': 'Suzanne Vega',
    'season': 3,
    'episode': 8
}, {
    'text': 'There can be no progress without head-on confrontation.',
    'author': 'Christopher Hitchens',
    'season': 3,
    'episode': 9
}, {
    'text': 'Sometimes it\'s necessary to go a long distance out of the way to come back a short distance correctly.',
    'author': 'Edward Albea',
    'season': 3,
    'episode': 10
}, {
    'text': 'Stagnation is death. If you don\'t change, you die. It\'s that simple. It\'s that scary.',
    'author': 'Leonard Sweet',
    'season': 3,
    'episode': 11
}, {
    'text': 'In my opinion, actual heroism, like actual love, is a messy, painful, vulnerable business.',
    'author': 'John Green',
    'season': 3,
    'episode': 12
}, {
    'text': 'Maybe all one can do is hope to end up with the right regrets.',
    'author': 'Arthur Miller',
    'season': 3,
    'episode': 13
},{
    'text': 'If you have behaved badly, repent, make what amends you can and address yourself to the task of behaving better next time.',
    'author': 'Aldous Huxley',
    'season': 4,
    'episode': 1
}, {
    'text': 'Sooner or later everyone sits down to a banquet of consequences.',
    'author': 'Robert Louis Stevenson',
    'season': 4,
    'episode': 2
}, {
    'text': 'We are all in the same boat, in a stormy sea, and we owe each other a terrible loyalty.',
    'author': 'G.K. Chesterton',
    'season': 4,
    'episode': 3
}, {
    'text': 'In our quest for the answers of life we tend to make order out of chaos, and chaos out of order.',
    'author': 'Jeffrey Fry',
    'season': 4,
    'episode': 4
}, {
    'text': 'There are many ways of going forward, but only one way of standing still.',
    'author': 'Franklin D. Roosevelt',
    'season': 4,
    'episode': 5
}, {
    'text': 'Truth is outside of all patterns.',
    'author': 'Bruce Lee',
    'season': 4,
    'episode': 6
}, {
    'text': 'By imposing too great a responsibility, or rather, all responsibility, on yourself, you crush yourself.',
    'author': 'Franz Kafka',
    'season': 4,
    'episode': 7
}, {
    'text': 'How few there are who have courage enough to own their faults, or resolution enough to mend them.',
    'author': 'Benjamin Franklin',
    'season': 4,
    'episode': 8
}, {
    'text': 'Resistance is useless.',
    'author': 'Doctor Who',
    'season': 4,
    'episode': 9
}, {
    'text': 'Happiness does not depend on outward things, but on the way we see them.',
    'author': 'Leo Tolstoy',
    'season': 4,
    'episode': 10
}]


def main():
    quote = random.choice(QUOTES)
    text = textwrap.fill(quote['text'])
    author = quote['author']
    print('{}\n-- {}'.format(text, author))


if __name__ == '__main__':
    main()
