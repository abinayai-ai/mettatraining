; what is atomspace

; AtomSpace represents knowledge in the form of Atoms, the fundamental building block of all the data.


; !(Hello World!)

; Pattern Matching
; - table, pattern, output
; - space, pattern, output

(Parent Tom Bob) ; Tom is the parent of Bob
(Parent Bob Ann)
(Parent Ann Bub)
;pattern to search for: Ann is the parent of Bub
;output to return: data found!

!(match &self (Parent Tom Bobby) (Tom is Bobs Parent))
!(match &self (Parent Ann Bub) (data found!))

; Question: who is the grandparent of Bub?
; nested query
!(match &self (Parent $x Bub) 
    (match &self (Parent $y $x) 
        ($y is the Grandparent of Bub)))
; add-atom, remove-atom
!(add-atom &self (Parent Monica Bob))

!(match &self (Parent Monica Bob) (Parent Monica Bob))
!(remove-atom &self (Parent Ann Bub))
!(match &self (Parent Ann Bub) (Parent Ann Bub))