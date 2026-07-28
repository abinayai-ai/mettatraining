

; how to write let expression

!(let $x (this is x value) $x)

; how to write a function

(= (myFun) (this is inside my function))

!(myFun)

; function with parameter

(= (myfunc $x) (this is number $x))

!(myfunc 4)


; function that check weather a numebr is even or not
(= (isEven $x) 
   (if (== (% $x 2) 0) True False)
)

!(isEven 2)

; how to write a recursion function

(= (factorial $x)
   (if (== $x 0)
       1
       (let $val (- $x 1)
            (* $x (factorial $val)))))

!(factorial 3)


; (: filter (-> (-> $a Bool) (List $a) (List $a)))


; (= (filter $p Nil) Nil)
; (= (filter $p (Cons $x $xs)) (if ($p $x) (Cons $x (filter $p $xs)) (filter $p $xs)))

; ! (filter isEven (Cons 1 (Cons 2 (Cons 3 (Cons 4 (Cons 5 Nil))))))


(= (filter $id ()) ())
(= (filter $id $list)
   (let* (
      ($first (car-atom $list))
      ($rest (cdr-atom $list))
   )
   (if ($id $first)
       (let $filtered-rest (filter $id $rest)
            (cons-atom $first $filtered-rest))
       (filter $id $rest))))


!(filter isEven (1 2 3 4 5))

(= (foldl $acc ()) $acc)
(= (foldl $acc $list)

(let* (
    ($first (car-atom $list))
    ($rest (cdr-atom $list))
    ($res (+ $acc $first))
)
  (foldl $res $rest)
)
)

!(foldl 0 (1 2 3 4))

