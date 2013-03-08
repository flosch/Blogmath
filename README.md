Blogmath
========

A simple sample compiler - see my compiler course at http://blog.florian-schlachter.de/2013/02/compilerbau-grundlagen.html

Usage
=====

	$ cat test1.bm
	var c = 2; // Exponent
  
	var s = 0.5;
	
	// Funktion zur Potenzierung
	lambda pow(a) = a^c;
	// Funktion zum Wurzelziehen
	lambda sqrt(a) = a^s;
	
	// Ergebnis berechnen von 5^2
	var result = pow(5);
	// Ergebnis berechnen von 25^0.5
	var result2 = sqrt(result);
	
	// Ergebnis ausgeben
	print(result); // Gibt 25 aus
	print(result2); // Gibt 5 aus
	
	
	$ python blogmath.py test1.bm
	Blogmath-Interpreter
	Executing test1.bm...
	25.0
	5.0
	
	
	$ python blogmath.py
	Blogmath-Interpreter
	('quit' or CTRL-C to terminate)
	> lambda pow(x, y) = x^y;
	> lambda sqrt(x) = x^0.5;
	> var hundert = pow(10, 2);
	> print(hundert);
	100.0
	> print(sqrt(hundert));
	10.0
	> lambda pow10(x) = pow(x, 10);
	> pow10(2);
	1024.0
	> print(2+12/2);
	8.0
	> print(5+4/3); // ohne Klammerung
	6.33333333333
	> print((5+4)/3); // mit Klammerung
	3.0
	> quit
