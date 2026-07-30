!(bind! math (py-atom math))
!(bind! os (py-atom os))
!(bind! query (py-atom query))

!(println ((math pow) 2 10))

!(println ((os cpu_count)))

!(println ((query unique_items) (1 2 2 3 3 4 5 5)))