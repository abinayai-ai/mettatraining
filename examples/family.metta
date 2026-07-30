
(Parent Tom Bob)
(Parent Bob Ann)
(Parent Ann Liz)

(= (parent $x) (match &self (Parent $y $x) $y))
(= (grandparent $x) (parent (parent $x)))