;; Identity function
(= (id $x) $x)

;; General accumulator
(= (accumulate $combiner $baseCase $f $a $b)
   (if (> $a $b)
       $baseCase
       ($combiner
           ($f $a)
           (accumulate
               $combiner
               $baseCase
               $f
               (+ $a 1)
               $b))))

;; Test
!(accumulate + 0 id 1 4)
