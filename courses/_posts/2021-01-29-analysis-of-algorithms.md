---
layout: post
title:  "Analysis of Algorithms (Coursera)"
tags:   algorithms coursera
date:   2021-01-29 16:00:30 -0500
---

I came across Erik Demaine's [*Advanced Data Structures*](https://www.youtube.com/watch?v=T0yzrZL1py0&list=PLUl4u3cNGP61hsJNdULdudlRL493b-XZf) videos recently, which led me back to more fundamental materials. I'm trying a new format of posting Markdown notes, where the post serves as a bit of course review, but mainly as a collection of pointers for my own recall purposes (e.g. in situations like "what was that theorem referred to in that class, again?").

Sedgewick doesn't need much of an introduction, and Coursera is reliable as always. This course assumes a fair bit of comfort with "math for computer science" type materials, which I had to review independently (I still found many of the mathetmatical derivations to be insufficiently motivated or explained to follow). There are brief quizzes, which are helpful, though the assignments just refer to exercises from [Sedgewick's book](https://aofa.cs.princeton.edu/home/) (which is understandable, since most answers are not in a simple form that can be auto-graded). I ended up skimming the later weeks for high-level concepts and interesting applications, just to get some familiarity with the problem space.


|             | Analysis of Algorithms                                             |
|:------------|:-------------------------------------------------------------------|
| Source      | [Coursera](https://www.coursera.org/learn/analysis-of-algorithms/) |
| Author      | Robert Sedgewick (Princeton)                                       |
| Free        | Yes                                                                |
| Videos      | Yes                                                                |
| Quizes      | Yes (graded)                                                       |
| Assignments | Yes (ungraded; exercises from book)                                          |
| Resources   | [Booksite](https://aofa.cs.princeton.edu/home/)                    |


<hr>

# Week 1: Intro

Asymptotic complexity from theory of algorithms isn't everything. It does not provide a basis for compariing algorithms directly or for predicting performance, insofar as actual execution and practicality may vary widely (due to constants, input assumptions, implementation difficulty, etc).

Analysis of algorithms (AofA) provides means for predicting performance (Babbage: "how many times will we need to turn the crank to power the computer?") and potentially yielding improvements.

Modern pioneer -- Knuth in 1960s (see *Art of Computer Programming*)

Examples

- QuickSort $$O(N^2)$$ in worst case vs MergeSort $$O(NlogN)$$; in practice, former can be twice as fast 
- [Chazelle's polygon triangulation](https://en.wikipedia.org/wiki/Polygon_triangulation#:~:text=Computational%20complexity,-Until%201988%2C%20whether&text=Bernard%20Chazelle%20showed%20in%201991,expected%20time%20is%20also%20known.) -- theoretical achievement of provably linear-time, but too complex to implement

Instead of big-O (or omega or theta), AofA uses tilde notation:
$$g(N) \sim f(N)\iff|g(N)/f(N)|\rightarrow 1\ \ as\ \ N\rightarrow\infty$$

For quicksort, number of comparisons is $$\sim 2NlnN - 2(1-\gamma)N $$


<hr>

# Week 2: Recurrences

**Telescoping**

Linear first-order recurrences (constant coefficient, only one term on RHS) always evaluate to a sum (need to know how to evaluate discrete sums).

When coefficient not 1, divide by summation factor. For $$ a_n = X_na_{n-1} + ... $$, divide by product $$X_nX_{n-1}...X_1$$ to cancel out factors.

---

**Example (Quiz)**

- Solve recurrence for $$a_n = na_{n-1} + n!\ for \ n>0\ and\ a_0=1$$.

Approach 1 (initial values)

- $$a_0=1$$, $$a_1=1*1 + 1! = 2 = 2!$$, $$a_2=2*2 + 2! = 6 = 3!$$, $$a_3=3*6 + 3! = 24 = 4!$$
- By solving initial values, we observe that $$a_n = (n+1)!$$

Approach 2 (summation factor)

- Applying the formula for summation factor: product $$n(n-1)(n-2)...1$$, or $$n!$$
- Applying the summation factor as divisor on both sides: $$a_n / n! = (na_{n-1} + n!)/n!$$, or $$a_n/n! = a_{n-1}/(n-1)! + 1$$
- Telescope: $$a_n/n! = a_{n-1}/(n-1)! + 1 = a_{n-2} / (n-2)! + 1 + 1 = a_0/0! + 1 + ...  + 1 $$
- Since there are n+1 terms of 1 on the RHS, $$a_n/n! = n+1 \rightarrow a_n = (n+1)!$$

---


Other types of recurrences: {first order, second order, higher order} x {inear, non-linear, variable coefficients}... full history, divide and conquer

Number of compares for mergesort: $$\sim N\lfloor lgN \rfloor - 2^{\rfloor lgN \rfloor + 1}  + 2N$$

[Master theorem](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))

[Quicksort vs Mergesort comparisons plot](https://github.com/tkuriyama/tkuriyama.github.io/blob/master/notebooks/Quicksort_vs_Mergesort.ipynb)

<hr>

# Week 3: Generating Functions

Ordinary generating function (OGF) is of form $$A(z) = \sum\limits_{k>=0} {a_kz^k}$$

e.g. the constant sequence $$1, 1, 1, 1...$$ can be modeled by the coefficients of the geometric series $$1, x, x^2, x^3... = 1/(1-x)\ where\ \mid x \mid <1$$

A gentler [introduction to generating functions](https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-042j-mathematics-for-computer-science-fall-2010/readings/MIT6_042JF10_chap12.pdf)

[Catalan numbers](https://en.wikipedia.org/wiki/Catalan_number), e.g.
- how many gambler's ruin sequences with N wins?
- how many ways to triangulate a (N+1)-agon?
- how many binary trees with N nodes?
- how many trees with N+1 nodes?

Expected number of leaves in random tree of size N: using generating functions, ~N/4

---

**solving recurrence Example (Quiz)** 

Suppose $$a_n= 9a_{n−1} − 20a_{n−2}\ for\ n>1\ with\ a_0=0​\ and\ a_1=1$$; what is the value of $$\lim\limits_{n\rightarrow\infty}a_n/a_{n-1}$$?

- Make valid for all N: $$a_n= 9a_{n−1} − 20a_{n−2} + \delta_{n1}$$
- Multiply by $$z^n$$ and sum on $$n$$ (with right-shifts for n-1, n-2): $$A(z) = 9zA(z) - 20z^2A(z) + z$$
- Rearranging: $$A(z) = \frac{z}{1-9z + 20z^2}$$
- Factoring the denominator into partial fractions: $$A(z) = \frac{c_0}{5x-1} + \frac{c_1}{4x-1}$$
- The numerator is then $$c_0(4x-1) + c_1(5x-1)$$, which rewrites to $$-c_0 - c_1 + (4c_0 + 5c_1)x = x$$, so lining up the polynomial factors, $$-c_0-c_1 = 0$$ and $$4c_0+5c_1 = 1$$, yielding $$c_0 = -1, c_1 = 1$$
- Applying the above, we have $$A(z) = \frac{1}{4z-1} - \frac{1}{5z-1}$$
- Rearranging to the familiar form: $$A(z) = \frac{1}{1-5z} - \frac{1}{1-4z}$$
- Expanding the familiar series: $$a_n = 5^n - 4^n$$

So the limit of $$a\_n/a_{n-1}$$ is the limit of $$\frac{5^n - 4^n}{5^{n-1} - 4^{n-1}}$$, and since the powers of 4 become asymptotically insignifant, the limit is the ratio of $$5^n / 5^{n-1} = 5 $$


<hr>

# Week 4: Asymptotics

Goal -- develop expansion for expressions, on the standard scale (powers, logs...), which may be otherwise difficult to compute / compare

Various techniques: simplification, substitution, multiplication, division, etc, often using known series an lemmas

---

**Asymptotic Expansion Lemmas**

- Exp / log manipulation: $$(1+1/N)^N =exp(ln((1+1/N)^N)) = exp(N\ ln(1+1/n))$$
- Taylor series expansion for $$ln(1+x)$$: $$1/n - O(1/n^2)$$ (more terms for precision)
- Lemma: $$e^{O(1/N)} = 1 + O(1/N)$$

 ---
 
[Euler-Maclaurin summation]( https://en.wikipedia.org/wiki/Euler%E2%80%93Maclaurin_formula) for finite sums

<hr>

# Week 5: Analytical Combinatorics

Symbolic method: define and transform combinatorial constructions to generating functions (GFs)

Constructions (Classes)
- $$Z$$ - atom of size 1
- $$E$$ - atom of size zero (neutral class)
- $$\phi$$ - empty class

Examples (of counting sequence -- how many objects of each size? --> OGF)
- natural numbers: $$I_n = 1 \rightarrow 1/(1-z)$$
- bitstrings: $$B_n = 2^n \rightarrow 1/(1-2z)$$

Labelled vs unlabelled combinatorics

Labelled classes use exponential generating functions since labels introduce many more combinations
- urn = collection of atoms
- e.g. a permutation can be defined as a sequence of lableled atoms, counting equence is N!, for EGF of $$1/(1-z)$$

A permutation is a set of cycles: $$ SET(CYCLE(Z)) \rightarrow exp(ln(1/(1-z))$$, whose EGF counting function is $$N!$$

Derangements problem
- N people go to the opera and leave their hats on a shelf in the cloakroom... what is probability that noone gets their own hat?
- A permutation with no singleton cycles!
- Definition: $$D = SET(CYC_{>1}(Z))$$
- Transforming and expanding: $$D = e^{z^2/2 + z^3/3..} = exp(ln(1/(1-z) - z) = e^{-z} / (1-z) = ~1/e$$

<hr>

# Week 6: Trees and Forests

How many forests with N nodes? (Catalan numbers, 1, 2, 5, 15...)
- same as number of trees with N nodes
- $$F=SEQ(G)$$ and $$G=ZxF$$
- Translate directly to OGF: $$F(z)=1/(1-G(z)$$ and $$ G(z) = zF(z)$$
- Same Catalan numbers as before: $$F(z) - zF(z)^2 = 1 \rightarrow \ \sim\frac{4^{N-1}}{\sqrt{\pi N^3}}$$

BST shape depends on insertion order; shape is a property of permutation (given size N), not trees

How many permutations map to a general binary tree t (of a particular shape)?
- Let $$P_t$$ be the count of permutations that map to t
- $$P_t$$ is the number of ways to intermix left and right subtrees, multiplied by the count of permutations of the left and right subtrees

$$P_t = {\mid t_{l} \mid + \mid t_{r} \mid \choose \mid t_{l} \mid} \cdot P_{tl} \cdot P_{tr} $$

BST and Quicksort bijection
- expected internal path length in BST built from random permutation: $$\sim 2Nlg(N)$$
- average # of compares for qicksort = average external path length in BST built from random permutation = average internal path length + 2N

<hr>

# Week 7: Permutations

A permutation is a mapping of numbers 1 through n to itself.
- an inverse of the mapping can therefore be considered
- in a lattice representation, the inverse is the transposition

A permutation is a set of cycles

Random permutation algorithm (Knuth)
- move from left to right; exchange each item with a random item on its right
-all permutations equally likely: algorithm models construction of N! possibilities 

Involution
- Inverse of an involution is itself
- Involution is the mapping of numbers 1 - N to itself through 1 or 2 cycles

[100 prisoners problem](https://en.wikipedia.org/wiki/100_prisoners_problem); always follow cycle for ~31% chance success! (same as probability that there are no cycles longer than 50 in the permutation)

For permtutations, EGFs can be used as OGFs to extract expected value (since the $$N!$$ is also the counting sequence)


<hr>

# Week 8: Strings and Tries

(Unambigous) grammer to OGF mapping, e.g. if A and B are unambigous regular expressions with OGFs A(z) and B(z)...

- A + B -> A(z) + B(z)
- AB -> A(z)B(z)
- A* -> 1/(1-A(z))

Example: binary strings representing multiples of 3
- RE: (1(01*0)*10*)*
- Applying OGF mapping from above

$$D_3(z) = 1/(...) = 1 - \frac{z^2}{(1-2z)(1+z)} = \sim\frac{2^{N-1}}{3}$$


Trie: a binary tree where leaves may be void (though siblings of a void node cannot be void)
- can be used e.g. to represent set of bitstrinsg
- path from root to leaf represents bit string, where left is 0 and right is 1;  prefix free sets of strings (unless using non-void internal nodes)
- can also build things like suffix multi-way trie to answer quesions like "is this substring present in the given string?"

Pr(root is of rank k)
- BST: $$1/N$$
- Trie: binomial $$\frac{1}{2^N}{N \choose k}$$ (for N strings, probability that k of them start with n)


<hr>

# Week 9: Words and Mappings

Analytical combinatoris approach to birthday problem
- On average, how many people asked before finding two with same birthday?
- Probabilty that no char is repeated in a random M-word of length N: $$\frac{M!}{M^N(M-N)!}$$
- Summing and using Laplace method for Ramanajan Q function from asymptotics lecture: $$1+Q(M) \sim \sqrt{\pi M/2}$$
- With M=365, about 24

Coupon collector problem
- Can use OGF to solve and alos analyze variance: M-word with no empty set $$SEQ_M(SET_{>0}Z)$$ 
- Classical solution
- Probability that j rolls are needed to get (k+1)st coupon: $$(k/M)^j$$
- Expected number of rolls to get the (k+1)st coupon: $$\sum\limits_{j>=0} {(k/M)^j = 1/(1 - k/M) = M/(M-k)}$$
- Expected number of rolls to get all coupons: $$\sum\limits_{0<k<=M} M/(M-k) = MH_M = \sim MlgM $$

[Linear probing]([Linear probing](https://en.wikipedia.org/wiki/Linear_probing#:~:text=Linear%20probing%20is%20a%20scheme,by%20Gene%20Amdahl%2C%20Elaine%20M._)

Mapping
- how many N words with length N?
- Can form directed graphs from mappings -- what are the properties thereof?

