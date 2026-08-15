// 100% Dynamic PDF Reconstruction Engine [kemh_template.typ]
#import "./kemh_template.typ": *

#show: ncert-document.with(
  chapter-num: "2",
  chapter-title: "RELATIONS AND FUNCTIONS"
)

#ncert-page-one-opening(
  unit-num: "2",
  title: "RELATIONS AND FUNCTIONS",
  quote-text: "vMathematics is the indispensable instrument of"
)

  #ncert-h2("all physical research. – BERTHELOT v")

  #ncert-h1("2.1  Introduction")

  Much of mathematics is about finding a pattern – arecognisable link between quantities that change. In ourdaily life, we come across many patterns that characteriserelations such as brother and sister, father and son, teacherand student. In mathematics also, we come across manyrelations such as number m is less than number n, line l isparallel to line m, set A is a subset of set B. In all these, wenotice that a relation involves pairs of objects in certainorder. In this Chapter, we will learn how to link pairs ofobjects from two sets and then introduce relations betweenthe two objects in the pair. Finally, we will learn aboutspecial relations which will qualify to be functions. Theconcept of function is very important in mathematics since it captures the idea of amathematically precise correspondence between one quantity with the other.

  #ncert-h1("2.2  Cartesian Products of Sets")

  Suppose A is a set of 2 colours and B is a set of  3 objects, i.e.,

  A = {red, blue}and B = {b, c, s},where b, c and s represent a particular bag, coat and shirt, respectively.How many pairs of coloured objects can be made from these two sets?Proceeding in a very orderly manner, we can see that there will be 6distinct pairs as given below:

  #ncert-h2("(red, b), (red, c), (red, s), (blue, b), (blue, c), (blue, s).")

  Thus, we get 6 distinct objects (Fig 2.1).Let us recall from our earlier classes that an ordered pair of elementstaken from any two sets P and Q is a pair of elements written in small

  #ncert-h2("Fig 2.1")

  #ncert-h1("Chapter 2")

  #ncert-h2("G . W.  Leibnitz")

  #ncert-h2("(1646–1716)")

  Reprint 2026-27

  brackets and grouped together in a particular order, i.e., (p,q), p ∈ P and  q ∈ Q . Thisleads to the following definition:

  #ncert-green-box(title: "", [Definition 1 Given two non-empty sets P and Q. The cartesian product P × Q is theset of all ordered pairs of elements from P and Q, i.e.,])

  P × Q = { (p,q) : p  ∈ P, q  ∈ Q }If either P or Q is the null set, then P × Q will also be empty set, i.e., P × Q = φ

  From the illustration given above we note thatA × B = {(red,b), (red,c), (red,s), (blue,b), (blue,c), (blue,s)}.Again, consider the two sets:A = {DL, MP, KA}, where DL, MP, KA represent Delhi,Madhya Pradesh and Karnataka, respectively and B = {01,02,03}representing codes for the licence plates of vehicles issuedby DL, MP and KA .

  If the three states, Delhi, Madhya Pradesh and Karnatakawere making codes for the licence plates of vehicles, with therestriction that the code begins with an element from set A,which are the pairs available from these sets and how many suchpairs will there be (Fig 2.2)?

  The available pairs are:(DL,01), (DL,02), (DL,03), (MP,01), (MP,02), (MP,03),(KA,01), (KA,02), (KA,03) and the product of set A and set B is given byA × B = {(DL,01), (DL,02), (DL,03), (MP,01), (MP,02), (MP,03), (KA,01), (KA,02),

  (KA,03)}.It can easily be seen that there will be 9 such pairs in the Cartesian product, sincethere are 3 elements in each of the sets A and B. This gives us 9 possible codes. Alsonote that the order in which these elements are paired is crucial. For example, the code(DL, 01) will not be the same as the code (01, DL).

  As a final illustration, consider the two sets A= {a1, a2} andB = {b1, b2, b3, b4} (Fig 2.3).

  #ncert-h2("A × B = {( a1, b1), (a1, b2), (a1, b3), (a1, b4), (a2, b1), (a2, b2),")

  (a2, b3), (a2, b4)}.The 8 ordered pairs thus formed can represent the position of points inthe plane if A and B are subsets of the set of real numbers and it isobvious that the point in the position (a1, b2) will be distinct from the pointin the position (b2, a1).

  #ncert-h2("Remarks")

  (i)Two ordered pairs are equal, if and only if  the corresponding first elementsare equal and the second  elements are also equal.

  #ncert-h2("DLMPKA")

  #ncert-h2("0302")

  #ncert-h2("01")

  #ncert-h2("Fig 2.2")

  #ncert-h2("Fig 2.3")

  Reprint 2026-27

  26MATHEMATICS

  (ii)If there are p elements in A and q elements in B, then there will be pqelements in A × B, i.e.,  if n(A) = p and n(B) = q,  then n(A × B) = pq.(iii)If A and B are non-empty sets and either A or B is an infinite set, then so is

  A × B.

  #ncert-h2("(iv)A × A × A = {(a, b, c) : a, b, c ∈ A}. Here (a, b, c) is called an ordered")

  #ncert-h2("triplet.")

  #ncert-h2("Example 1 If  (x + 1, y – 2) = (3,1), find the values of x and y.")

  Solution Since the ordered pairs are equal, the corresponding elements are equal.Thereforex + 1 = 3  and y – 2 = 1.

  #ncert-h2("Solving we getx = 2 and y = 3.")

  #ncert-problem-box(title: "Example", [Example 2 If P = {a, b, c} and Q = {r}, form the sets P × Q and Q × P.Are these two products equal?])

  #ncert-h2("Solution By the definition of the cartesian product,")

  P × Q =  {(a, r), (b, r), (c, r)} and Q × P =  {(r, a), (r, b), (r, c)}Since, by the definition of equality of ordered pairs, the pair (a, r) is not equal to the pair(r, a), we conclude that P × Q ≠ Q × P.However, the number of elements in each set will be the same.

  #ncert-h2("Example 3 Let A = {1,2,3}, B = {3,4} and C = {4,5,6}. Find")

  (i)A × (B ∩ C)(ii)(A × B) ∩ (A × C)(iii)A × (B ∪ C)(iv)(A × B) ∪ (A × C)

  #ncert-h2("Solution (i) By the definition of the intersection of two sets, (B ∩ C) = {4}.")

  Therefore, A × (B ∩ C) = {(1,4), (2,4), (3,4)}.

  (ii)Now (A × B) = {(1,3), (1,4), (2,3), (2,4), (3,3), (3,4)}

  and   (A × C) = {(1,4), (1,5), (1,6), (2,4), (2,5), (2,6), (3,4), (3,5), (3,6)}Therefore,(A × B) ∩ (A × C)  = {(1, 4), (2, 4), (3, 4)}.

  (iii) Since,(B ∪ C) = {3, 4, 5, 6}, we haveA × (B ∪ C) = {(1,3), (1,4), (1,5), (1,6), (2,3), (2,4), (2,5), (2,6), (3,3),(3,4), (3,5), (3,6)}.

  (iv) Using the sets A × B and A × C from part (ii) above, we obtain

  (A × B) ∪ (A × C) = {(1,3), (1,4), (1,5), (1,6), (2,3), (2,4), (2,5), (2,6),(3,3), (3,4), (3,5), (3,6)}.

  Reprint 2026-27

  #ncert-h2("Example 4 If P = {1, 2}, form the set P × P × P.")

  #ncert-h2("Solution We have,  P × P × P =  {(1,1,1), (1,1,2), (1,2,1), (1,2,2), (2,1,1), (2,1,2), (2,2,1),")

  #ncert-h2("(2,2,2)}.Example 5 If R is the set of all real numbers, what do the cartesian products R × R")

  #ncert-h2("and R × R × R represent?")

  Solution The Cartesian product R × R represents the set R × R={(x, y) : x, y ∈ R}which represents the coordinates of all the points in two dimensional space and thecartesian product R × R × R represents the set R × R × R ={(x, y, z) : x, y, z ∈ R}which  represents the coordinates of all the points in three-dimensional space.

  #ncert-h2("Example 6 If A × B ={(p, q),(p, r), (m, q), (m, r)}, find A and B.")

  #ncert-h2("SolutionA = set of first elements = {p, m}B = set of second elements = {q, r}.")

  #ncert-h2("EXERCISE 2.1")

  #ncert-h2("1.If")

  #ncert-h2("25 11333 3x,y –,+=, find the values of x and y.")

  2.If the set A has 3 elements and the set B = {3, 4, 5}, then find the number ofelements in (A×B).3.If G = {7, 8} and H = {5, 4, 2}, find G × H and H × G.4.State whether each of the following statements are true or false. If the statementis false, rewrite the given statement correctly.

  (i)If P = {m, n} and Q = { n, m}, then P × Q = {(m, n),(n, m)}.(ii)If A and B are non-empty sets, then A × B is a non-empty set of ordered

  pairs (x, y) such that x ∈ A and y ∈ B.(iii)If A = {1, 2}, B = {3, 4}, then A × (B ∩ φ) = φ.5.If A = {–1, 1}, find A × A × A.6.If A × B = {(a, x),(a , y), (b, x), (b, y)}. Find A and B.7.Let A = {1, 2}, B = {1, 2, 3, 4}, C = {5, 6} and D = {5, 6, 7, 8}. Verify that(i) A × (B ∩ C) = (A × B) ∩ (A × C). (ii) A × C is a subset of  B × D.8.Let A = {1, 2} and B = {3, 4}.  Write A × B. How many subsets will A × B have?List them.9.Let A and B be two sets such that n(A) = 3 and n(B) = 2.  If (x, 1), (y, 2), (z, 1)are in A × B, find  A and B, where x, y and  z are distinct elements.

  Reprint 2026-27

  28MATHEMATICS

  10.The Cartesian product A × A has 9 elements among which are found (–1, 0) and(0,1).  Find the set A and the remaining elements of A × A.

  #ncert-h1("2.3  RelationsConsider the two sets P = {a, b, c} and Q = {Ali, Bhanu, Binoy, Chandra, Divya}.The cartesian product ofP and Q has 15 ordered pairs whichcan be listed as P × Q = {(a, Ali),(a,Bhanu), (a, Binoy), ..., (c, Divya)}.")

  We can now obtain a subset ofP × Q by introducing a relation Rbetween the first element x and thesecond element y of each ordered pair(x, y) as

  R= { (x,y): x is the first letter of the name y, x ∈ P, y ∈ Q}.Then R = {(a, Ali), (b, Bhanu), (b, Binoy), (c, Chandra)}A visual representation of this relation R (called an arrow diagram) is shownin Fig 2.4.

  #ncert-green-box(title: "", [Definition 2 A relation R from a non-empty set A to a non-empty set B is a subset ofthe cartesian product  A × B. The subset is derived by describing a relationship betweenthe first element and the second element of the ordered pairs in A × B. The secondelement is called the image of  the first element.])

  #ncert-green-box(title: "", [Definition 3 The set of all first elements of the ordered pairs in a relation R from a setA to a set B is called the domain of the relation R.])

  #ncert-green-box(title: "", [Definition 4 The set of all second elements in a relation R from a set A to a set B iscalled the range of the relation R. The whole set B is called the codomain of therelation R. Note that range ⊂ codomain.])

  #ncert-h2("Remarks(i) A relation may be represented algebraically either by the Roster")

  #ncert-h2("method or by the Set-builder method.(ii) An arrow diagram is a visual representation of a relation.")

  #ncert-problem-box(title: "Example", [Example 7 Let A = {1, 2, 3, 4, 5, 6}. Define a relation R from A to A by])

  R = {(x, y) : y =  x + 1 }(i) Depict this relation using an arrow diagram.(ii) Write down the domain, codomain and range of R.

  #ncert-h2("Solution(i) By the definition of the relation,")

  #ncert-h2("R = {(1,2), (2,3), (3,4), (4,5), (5,6)}.")

  #ncert-h2("Fig 2.4")

  Reprint 2026-27

  The corresponding arrow diagram isshown in Fig 2.5.

  (ii) We can see that thedomain ={1, 2, 3, 4, 5,}

  Similarly, the range = {2, 3, 4, 5, 6}and the codomain = {1, 2, 3, 4, 5, 6}.

  #ncert-problem-box(title: "Example", [Example 8 The Fig 2.6 shows a relationbetween the sets P and Q. Write this relation (i) in set-builder form, (ii) in roster form.What is its domain and range?])

  #ncert-h2("Solution It is obvious that the relation R is")

  #ncert-h2("“x is the square of y”.")

  #ncert-h2("(i) In set-builder form, R = {(x, y): x")

  is the square of y, x ∈ P, y ∈ Q}(ii) In roster form, R = {(9, 3),

  (9, –3), (4, 2), (4, –2), (25, 5), (25, –5)}The domain of this relation is {4, 9, 25}.The range of this relation is {– 2, 2, –3, 3, –5, 5}.Note that the element 1 is not related to any element in set P.The set Q is the codomain of this relation.

  ANote  The total number of relations that can be defined from a set A to a set Bis the number of  possible subsets of A × B. If n(A ) =  p and n(B) = q, thenn (A × B) = pq and the total number of relations is 2pq.

  #ncert-problem-box(title: "Example", [Example 9 Let A = {1, 2} and B = {3, 4}. Find the number of relations from A to B.])

  #ncert-h2("Solution We have,")

  A × B = {(1, 3), (1, 4), (2, 3), (2, 4)}.Since n (A×B ) = 4, the number of subsets of A×B is 24. Therefore, the number ofrelations from A into B will be 24.Remark  A relation R from A to A is also stated as a relation on A.

  #ncert-h2("EXERCISE 2.2")

  1.Let A = {1, 2, 3,...,14}. Define a relation R from A to A byR = {(x, y) : 3x – y = 0, where x, y ∈ A}. Write down its domain, codomain andrange.

  #ncert-h2("Fig 2.5")

  #ncert-h2("Fig 2.6")

  Reprint 2026-27

  30MATHEMATICS

  2.Define a relation R on the set N of natural numbers by R = {(x, y) : y =  x + 5,

  x is a natural number less than 4; x, y ∈N}. Depict this relationship using rosterform. Write down the domain and the range.

  3.A = {1, 2, 3, 5} and B = {4, 6, 9}. Define a relation R from A to B byR = {(x, y): the difference between x and y is odd; x ∈ A, y ∈ B}. Write R inroster form.

  #ncert-h2("4.The Fig2.7 shows a relationshipbetween the sets P and Q. Write thisrelation")

  (i) in set-builder form (ii) roster form.What is its domain and range?5.Let A = {1, 2, 3, 4, 6}. Let R be therelation on A defined by{(a, b): a , b ∈A, b is exactly divisible by a}.

  (i)Write R in roster form

  (ii)Find the domain of R

  (iii)Find the range of R.6.Determine the domain and range of the relation R defined byR = {(x, x  + 5) : x ∈ {0, 1, 2, 3, 4, 5}}.7.Write the relation R = {(x, x3) : x is a prime number less than 10} in roster form.8.Let A = {x, y, z} and B = {1, 2}. Find the number of relations from A to B.9.Let R be the relation on Z defined by R = {(a,b): a,  b ∈ Z, a – b is an  integer}.Find the domain and range of R.

  #ncert-h1("2.4FunctionsIn this Section, we study a special type of relation called function. It is one of the mostimportant concepts in mathematics. We can, visualise a function as a rule, which producesnew elements out of some given elements.  There are many terms such as ‘map’ or‘mapping’ used to denote a function.")

  #ncert-green-box(title: "", [Definition 5 A relation f from a set A to a set B is said to be a function if everyelement of set A has one and only one image in set B.])

  In other words, a function f is a relation from a non-empty set A to a non-emptyset B such that the domain of f is A and no two distinct ordered pairs in f  have thesame first element.

  If f is a function from A to B and (a, b) ∈ f, then f (a) = b, where b is called theimage of a under f and a is called the preimage of b under f.

  #ncert-h2("Fig 2.7")

  Reprint 2026-27

  The function f from A to B is denoted by f: A à B.Looking at the previous examples, we can easily see that the relation in Example 7 isnot a function because the element 6 has no image.

  Again, the relation in Example 8 is not a function because the elements in thedomain are connected to more than one images. Similarly, the relation in  Example 9 isalso not a function. (Why?) In the examples given below, we will see many morerelations some of which are functions and others are not.

  #ncert-problem-box(title: "Example", [Example 10 Let N be the set of natural numbers and the relation R be defined onN such that  R = {(x, y) : y = 2x, x, y ∈ N}.])

  What is the domain, codomain and range of R? Is this relation a function?

  Solution The domain of R is the set of natural numbers N. The codomain is also N.The range is the set of even natural numbers.

  #ncert-h2("Since every natural number n has one and only one image, this relation is afunction.")

  #ncert-problem-box(title: "Example", [Example 11 Examine each of the following relations given below and state in eachcase, giving reasons whether it is a function or not?])

  (i)R = {(2,1),(3,1), (4,2)}, (ii) R = {(2,2),(2,4),(3,3), (4,4)}(iii)R = {(1,2),(2,3),(3,4), (4,5), (5,6), (6,7)}

  Solution (i)Since 2, 3, 4 are the elements of domain of R having their unique images,this relation R is a function.(ii)Since the same first element 2 corresponds to two different images 2and 4, this relation is not a function.(iii)Since every element has one and only one image, this relation is afunction.

  #ncert-green-box(title: "", [Definition 6 A function which has either R or one of its subsets as its range is calleda real valued function. Further, if its domain is also either R or a subset of R, it iscalled a real function.])

  #ncert-h2("Example 12 Let N be the set of natural numbers.  Define a real valued function")

  f : Nà N by f (x) = 2x + 1. Using this definition, complete the table given below.

  #ncert-h2("x1234567")

  yf (1) = ...f (2) = ...f (3) = ...f (4) = ...f (5) = ...f (6) = ...f (7) = ...

  #ncert-h2("Solution The completed table is given by")

  #ncert-h2("x1234567")

  yf (1) = 3f (2) = 5f (3) = 7f (4) = 9f (5) = 11f (6) = 13f (7) =15

  Reprint 2026-27

  32MATHEMATICS

  #ncert-h2("2.4.1  Some functions and their graphs(i)Identity function  Let R be the set of real numbers. Define the real valuedfunction f : R → R by y =  f(x) = x for each x ∈ R. Such a function is called theidentity function. Here the domain and range of f are R. The graph is a straight line asshown in Fig 2.8. It passes through the origin.")

  #ncert-h2("Fig 2.9")

  Fig 2.8(ii)Constant function Define the function f: R → R by y = f (x) = c, x ∈ R wherec is a constant and each x ∈ R. Here domain of f is R and its range is {c}.

  Reprint 2026-27

  The graph is a line parallel to x-axis. For example, if f(x)=3 for each x∈R, then itsgraph will be a line as shown in the Fig 2.9.

  (iii)Polynomial function A function f : R → R is said to be polynomial function iffor each x in R, y  =  f (x) = a0 + a1x  + a2x2 + ...+ an xn, where n is a non-negativeinteger and  a0, a1, a2,...,an∈R.

  The functions defined by f(x) = x3 – x2 + 2, and g(x) = x4 + 2 x are some examples

  #ncert-h2("of polynomial functions, whereas the function h defined by h(x) =")

  #ncert-h2("23x + 2x is not apolynomial function.(Why?)")

  #ncert-problem-box(title: "Example", [Example 13 Define the function f: R → R by y = f(x) = x2, x ∈ R. Complete theTable given below by using this definition. What is the domain and range of this function?Draw the graph of f.])

  #ncert-h2("x– 4–3–2–101234")

  #ncert-h2("y = f(x) = x2")

  #ncert-h2("Solution The completed Table is given below:")

  #ncert-h2("x– 4–3–2–101234")

  #ncert-h2("y = f (x) = x216941014916")

  #ncert-h2("Domain of f = {x : x∈R}. Range of f   = {x")

  #ncert-h2("2: x ∈ R}. The graph of f is givenby Fig 2.10")

  #ncert-h2("Fig 2.10")

  Reprint 2026-27

  34MATHEMATICS

  #ncert-h2("Example 14 Draw the graph of the function f :R → R defined by f (x) = x3, x∈R.")

  Solution We havef(0) = 0, f(1) = 1, f(–1) = –1, f(2) = 8, f(–2) = –8,  f(3) = 27; f(–3) = –27, etc.Therefore,   f = {(x,x3): x∈R}.The graph of f is given in Fig 2.11.

  #ncert-h2("Fig 2.11")

  #ncert-h2("(iv)Rational functions are functions of the type ( )( )f xg x , where f(x) and g(x) are")

  #ncert-h2("polynomial functions of x defined in a domain, where g(x) ≠ 0.")

  #ncert-h2("Example 15 Define the real valued function f : R – {0} → R defined by 1( ) =f xx ,")

  #ncert-h2("x ∈ R –{0}.  Complete the Table given below using this definition. What is the domainand range of this function?")

  #ncert-h2("x–2–1.5–1–0.50.250.511.52")

  #ncert-h2("y  = 1")

  #ncert-h2("x...........................")

  #ncert-h2("Solution The completed Table is given by")

  #ncert-h2("x–2–1.5–1–0.50.250.511.52")

  #ncert-h2("y = 1")

  #ncert-h2("x– 0.5– 0.67 –1– 24210.670.5")

  Reprint 2026-27

  The domain is all real numbers except 0 and its range is also all real numbersexcept 0. The graph of f is given in Fig 2.12.

  #ncert-h2("Fig 2.13")

  (v)The Modulus function The functionf: R→R defined by f(x) = |x| for eachx ∈R is called modulus function. For eachnon-negative value of x,  f(x) is equal to x.But for negative values of x, the value off(x) is the negative of the value of x, i.e.,

  #ncert-h2("0( )0x,xf xx,x")

  ≥= −\<

  The graph of the modulus function is givenin Fig 2.13.

  #ncert-h2("(vi)Signum function The functionf:R→R defined by")

  1 if0

  ( )0 if0

  1 if0

  #ncert-h2(",x")

  #ncert-h2("f x,x")

  #ncert-h2(",x")

  \>==−\<

  #ncert-h2("Fig 2.12")

  Reprint 2026-27

  36MATHEMATICS

  is called the signum function. The domain of the signum function is R and the range isthe set {–1, 0, 1}. The graph of the signum function is given by the Fig 2.14.

  #ncert-h2("Fig 2.14")

  (vii) Greatest integer functionThe function  f: R → R definedby f(x) = \[x\], x ∈R  assumes thevalue of the greatest integer, lessthan or equal to x. Such a functionis called the greatest integerfunction.

  #ncert-h2("From the definition of \[x\], wecan see that")

  \[x\] = –1 for –1 ≤ x \< 0\[x\] =   0 for 0 ≤ x \< 1\[x\] =   1 for 1 ≤ x \< 2\[x\] =   2 for 2 ≤ x \< 3 andso on.

  The graph of the function isshown in Fig 2.15.

  #ncert-h1("2.4.2   Algebra of real functions  In this Section, we shall learn how to add two realfunctions, subtract a real function from another, multiply a real function by a scalar(here by a scalar we mean a real number), multiply two real functions and divide onereal function by another.")

  (i)Addition of two real functions  Let f : X → R and g : X → R be any two realfunctions, where X ⊂ R. Then, we define (f + g): X → R by

  #ncert-h2("(f + g) (x) = f (x) + g (x), for all x ∈ X.")

  #ncert-h2("Fig 2.15")

  Reprint 2026-27

  (ii)Subtraction of a real function from another Let f : X → R and g: X → R beany two real functions, where X ⊂R. Then, we define (f – g) : X→R by(f–g) (x) = f(x) –g(x), for all x ∈ X.

  (iii)Multiplication by a scalar Let f : X→R be a real valued function and α be ascalar. Here by scalar, we mean a real number. Then the product α f is a function fromX to R defined by (α f ) (x) =  α f (x), x ∈X.

  (iv)Multiplication of two real functions The product (or multiplication) of two realfunctions f:X→R and g:X→R is a function fg:X→R defined by(fg) (x) = f(x) g(x), for all x ∈ X.This is also called pointwise multiplication.

  #ncert-h2("(v)Quotient of two real functions Let f and g be two real functions defined from")

  #ncert-h2("X→R, where X⊂R. The quotient of f by g denoted by")

  #ncert-h2("fg is a function defined by ,")

  #ncert-h2("( )( )( )ff xxgg x=, provided g(x) ≠ 0, x ∈ X")

  #ncert-h2("Example 16 Let f(x) = x")

  #ncert-h2("2and g(x) = 2x + 1 be two real functions.Find")

  #ncert-h2("(f + g) (x), (f –g) (x), (fg) (x),( )fxg.")

  #ncert-h2("Solution  We have,")

  #ncert-h2("(f + g) (x) = x")

  #ncert-h2("2 + 2x + 1, (f –g) (x) =  x2 – 2x – 1,")

  #ncert-h2("(fg) (x) = x")

  #ncert-h2("2 (2x + 1) = 2x3 + x2,  ( )fxg =")

  2

  #ncert-h2("21xx + , x  ≠ 12−")

  #ncert-problem-box(title: "Example", [Example 17 Let  f(x) = x and g(x) = x be two functions defined over the set of non-])

  #ncert-h2("negative real numbers. Find (f + g) (x), (f – g) (x), (fg) (x) and")

  #ncert-h2("fg (x).")

  #ncert-h2("Solution  We have")

  #ncert-h2("(f + g) (x) =  x + x, (f – g) (x)  = x  – x ,")

  #ncert-h2("(fg) x  =")

  #ncert-h2("32x( x )x= and ( )fxg")

  #ncert-h2("120–xx, xx==≠")

  Reprint 2026-27

  38MATHEMATICS

  #ncert-h2("EXERCISE 2.3")

  #ncert-h2("1.Which of the following relations are functions? Give reasons. If it is a function,determine its domain and range.")

  (i){(2,1), (5,1), (8,1), (11,1), (14,1), (17,1)}(ii){(2,1), (4,2), (6,3), (8,4), (10,5), (12,6), (14,7)}(iii){(1,3), (1,5), (2,5)}.2.Find the domain and range of the following real functions:

  #ncert-h2("(i)f(x) = – x(ii)f(x) = 29x−.")

  #ncert-h2("3.A function f is defined by f(x) = 2x –5. Write down the values of")

  (i) f (0),(ii)   f (7),    (iii)   f (–3).4.The function ‘t’ which maps temperature in degree Celsius into temperature in

  #ncert-h2("degree Fahrenheit is defined by t(C) = 9C")

  5  + 32.

  #ncert-h2("Find(i)t(0)      (ii)   t(28)     (iii)    t(–10)    (iv)  The value of C, when t(C) = 212.")

  #ncert-h2("5.Find the range of each of the following functions.")

  (i)f (x)  = 2 – 3x, x ∈ R, x \> 0.(ii) f (x)  = x2 + 2, x is a real number.(iii) f (x)  = x,  x is a real number.

  #ncert-h2("Miscellaneous Examples")

  #ncert-h2("Example 18  Let R be the set of real numbers.Define the real function")

  #ncert-h2("f: R→R by f(x) = x + 10")

  and sketch the graph of this function.

  #ncert-h2("Solution Here  f(0) = 10, f(1) = 11, f(2) = 12, ...,f(10) = 20, etc., and")

  f(–1) = 9, f(–2) = 8, ..., f(–10) = 0 and so on.Therefore, shape of the graph of the givenfunction assumes the form as shown in Fig 2.16.

  Remark The function f  defined by f(x) = mx + c ,x ∈ R, is called linear function, where m and c areconstants. Above function is an example of a linearfunction.Fig 2.16

  Reprint 2026-27

  #ncert-problem-box(title: "Example", [Example 19 Let R be a relation from Q to Q defined by R = {(a,b): a,b ∈ Q anda – b ∈ Z}. Show that])

  (i)(a,a) ∈ R for all a ∈ Q(ii)(a,b) ∈ R implies that (b, a) ∈ R(iii)(a,b) ∈ R and (b,c) ∈ R implies that (a,c) ∈R

  Solution(i)Since, a – a = 0 ∈ Z, if follows that (a, a) ∈ R.(ii)(a,b) ∈ R implies that a – b ∈ Z. So, b – a ∈ Z. Therefore,(b, a) ∈ R(iii)(a, b) and (b, c)  ∈ R implies that a – b ∈ Z. b – c ∈ Z.  So,      a – c = (a – b) + (b – c) ∈ Z. Therefore, (a,c) ∈ R

  #ncert-problem-box(title: "Example", [Example 20  Let f = {(1,1), (2,3), (0, –1), (–1, –3)} be a linear function from Z into Z.Find f(x).])

  Solution Since f is a linear function, f (x) = mx + c. Also, since (1, 1), (0, – 1) ∈ R,

  f (1) = m + c = 1 and f (0) = c = –1. This gives m = 2 and f(x) = 2x – 1.

  #ncert-h2("Example 21 Find the domain of the function")

  2

  #ncert-h2("235( )54xxf xxx++=−+")

  #ncert-h2("Solution  Since x")

  2 –5x + 4 = (x – 4) (x –1), the function f is defined for all real numbersexcept at x = 4 and x = 1. Hence the domain of f is R – {1, 4}.

  #ncert-h2("Example 22  The function f is defined by")

  #ncert-h2("f (x) =")

  1010

  10

  #ncert-h2("x, x")

  #ncert-h2(", x")

  #ncert-h2("x, x")

  −\<=+\>

  #ncert-h2("Draw the graph of f (x).")

  #ncert-h2("Solution Here,  f(x) = 1 – x, x \< 0, this gives")

  #ncert-h2("f(– 4) = 1 – (– 4)= 5;")

  #ncert-h2("f(– 3)=1 – (– 3) = 4,")

  #ncert-h2("f(– 2)= 1 – (– 2)= 3")

  #ncert-h2("f(–1)= 1 – (–1) = 2; etc,")

  #ncert-h2("andf(1) = 2, f (2) = 3, f (3) = 4")

  #ncert-h2("f(4) = 5 and so on for  f(x) = x + 1, x \> 0.")

  #ncert-h2("Thus, the graph of f is as shown in Fig 2.17Fig 2.17")

  Reprint 2026-27

  40MATHEMATICS

  #ncert-h2("Miscellaneous Exercise on Chapter 2")

  #ncert-h2("1.The relation  f is defined by")

  2 03( ) =

  3 310

  #ncert-h2("x ,xf x")

  #ncert-h2("x,x")

  ≤≤≤≤

  #ncert-h2("The relation g is defined by")

  2 , 02( )

  3 , 210

  #ncert-h2("xxg x")

  #ncert-h2("xx")

  #ncert-h2("≤≤=≤≤Show that f is a function and g is not a function.")

  #ncert-h2("2.If f (x) = x")

  #ncert-h2("2, find (1 1)(1)(1 1 1)f.– f. –.")

  #ncert-h2("3.Find the domain of the function f (x)")

  2

  #ncert-h2("221812xxx – x")

  ++=

  +.

  #ncert-h2("4.Find the domain and the range of the real function f defined by f (x)  = (1)x −.")

  #ncert-h2("5.Find the domain and the range of the real function f defined by f (x) = –1x.")

  #ncert-h2("6.Let")

  2

  #ncert-h2("2,:1xfxxx")

  #ncert-h2("=∈+R be a function from R into R. Determine the range")

  of f.7.Let f, g : R→R be defined, respectively by f(x) = x + 1, g(x) = 2x – 3. Find

  #ncert-h2("f  + g, f – g and")

  #ncert-h2("fg .")

  8.Let f = {(1,1), (2,3), (0,–1), (–1, –3)} be a function from Z to Z defined byf(x) = ax + b, for some integers a, b. Determine a, b.

  9.Let R be a relation from N to N defined by R = {(a, b) : a, b ∈N and a = b

  2}. Arethe following true?

  (i)(a,a) ∈ R, for all a ∈ N(ii)(a,b) ∈ R, implies (b,a) ∈ R(iii)(a,b) ∈ R, (b,c) ∈ R  implies (a,c) ∈ R.Justify your answer in each case.10.Let A ={1,2,3,4}, B = {1,5,9,11,15,16} and  f = {(1,5), (2,9), (3,1), (4,5), (2,11)}Are the following true?

  #ncert-h2("(i)f is a relation from A to B(ii)f  is a function from A to B.Justify your answer in each case.")

  Reprint 2026-27

  11.Let f be the subset of Z × Z defined by f = {(ab, a + b) : a, b ∈ Z}. Is f afunction from Z to Z? Justify your answer.12.Let A = {9,10,11,12,13} and let f : A→N be defined by f (n) = the highest primefactor of n. Find the range of f.

  #ncert-h2("Summary")

  #ncert-h2("A × B =  {(a, b): a ∈ A, b ∈ B}")

  #ncert-h2("In particular R × R = {(x, y): x, y ∈ R}")

  and R × R × R = {(x, y, z): x, y, z ∈ R}® If (a, b) = (x, y), then a = x and b = y.® If n(A) = p and n(B) = q, then n(A × B) = pq.® A × φ = φ® In general, A × B ≠ B × A.® Relation A relation R from a set A to a set B is a subset of the cartesian

  product A × B obtained by describing a relationship between the first elementx and the second element y of the ordered pairs in A × B.® The image of an element x under a relation R is given by y, where (x, y) ∈ R,® The domain of R is the set of all first elements of the ordered pairs in a

  relation R.® The range of the relation R is the set of all second elements of the ordered

  pairs in a relation R.® Function A function f from a set A to a set B is a specific type of relation for

  #ncert-h2("which every element x of set A has one and only one image y in set B.")

  We write f: A→B, where f(x) = y.® A is the domain and B is the codomain of f.

  Reprint 2026-27

  42MATHEMATICS

  ® The range of the function is the set of images.® A real function has the set of real numbers or one of its subsets both as its

  domain and as its range.® Algebra of functions For functions f : X  → R and g : X → R, we have

  #ncert-h2("(f + g) (x) = f (x) + g(x), x ∈ X")

  #ncert-h2("(f – g) (x) = f (x) – g(x), x ∈ X")

  #ncert-h2("(f.g) (x)    = f (x) .g (x), x ∈ X")

  #ncert-h2("(kf) (x)     = k ( f (x) ), x ∈ X, where k is a real number.")

  #ncert-h2("( )fxg")

  =

  #ncert-h2("( )( )f xg x , x ∈ X, g(x) ≠ 0")

  #ncert-h2("Historical Note")

  The word FUNCTION first appears in a Latin manuscript “Methodustangentium inversa, seu de fuctionibus” written by Gottfried Wilhelm Leibnitz(1646-1716) in 1673; Leibnitz used the word in the non-analytical sense. Heconsidered a function in terms of “mathematical job” – the “employee” beingjust a curve.

  On July 5, 1698, Johan Bernoulli, in a letter to Leibnitz, for the first timedeliberately  assigned a specialised use of the term function in the analyticalsense. At the end of that month, Leibnitz replied showing his approval.

  Function is found in English in 1779 in Chambers’ Cyclopaedia: “Theterm function is used in algebra, for an analytical expression any way compoundedof a variable quantity, and of numbers, or constant quantities”.

  #ncert-h1("— v —")

  Reprint 2026-27

