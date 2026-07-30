; !(functionName arg1 arg2 arg3 ...)

;; py-atom: allows obtaining a grounded atom for a Python object 
;;          imported from a given module or submodule.
; ! ((py-atom math.ceil) 3.14) ;imports math library and returns an atom asocciated with the math.ceil function
; ! ((py-atom math.floor) 10.5)
; ! ((py-atom numpy.absolute) -5)

; ! (bind! sum (py-atom sum)) ; this binds the atom returned by py-atom to the name sum
; !((py-atom sum) (py-atom "[1,2,3,4]"))

; ! (sum (py-atom "[1,2,3,4]")) ; this is the same as the python version of: sum([1,2,3,4])

; ; What if we wish to call functions from a submodule, say numpy.random? 
; ;; py-dot: py-dot operates with two arguments: it takes the first argument, 
; ;;         which is the grounded atom wrapping a Python object,
; ;;         and then searches for the value of an attribute within that 
; ;;         object based on the name provided in the second argument.
; ! (bind! np (py-atom numpy))
; ! ((py-dot np abs) -5) ;5
; ! ((py-dot np random.randint) 0 10 )


; ;; py-dot works on any Python Object
; ! ((py-dot "hello world" upper)) ; "hello world".upper() -> "HELLO WORLD"
; ! ((py-dot "Hello World" swapcase))

; !((py-dot "max" upper))

; ;; py-list, py-tuple and py-dict
; ! (py-dict (("a" "b") ("b" "c"))) ; creates a dict {"a":"b", "b":"c"}
; ! (py-tuple (1 5)) ; creates a tuple (1, 5)
; ! (py-list (1 (2 (3 "3")))) ; creates a nested list [1, [2, [3, '3']]]


! ((py-atom max) (py-list (-5 10 100 1000))) ; 1000