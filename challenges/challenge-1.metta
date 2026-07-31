; Identity function
(= (id $x) $x)

;; Check if a number is even
(= (isEven $x) (== (% $x 2) 0))

;; Higher-order conditional summation
(= (sumIf $f $condition $a $b)
   (if (> $a $b)
       0
       (if ($condition $a)
           (+ ($f $a) (sumIf $f $condition (+ $a 1) $b))
           (sumIf $f $condition (+ $a 1) $b))))

;; Test
!(sumIf id isEven 1 5)