class Solution(object):
    def generateParenthesis(self, n):
        """
        :type n: int
        :rtype: List[str]
        left right for 3 pairs
        left right, left right left right
        left  left right right left right
        left left left right right right

        ()()()
        (())()
        ((()))
        (()())
        
        cond5. itions:
        1. sum of left == sum right
        2. last one is right
        3. first one is left
        4. combinations must be unique
        5. at given point  sum of left parenthesis needs to be >= right parenthesis



        """
        l = "("
        r =")"

