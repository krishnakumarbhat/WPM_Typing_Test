class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        nums = ins_sort(nums)
        for i in range(len(nums)-1):
            if nums[i]==nums[i+1]:
                return True
            
        return False


class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        a = ord(s)
        t = ord(t)
        a =ins_sort(a)
        t = ins_sort(t)
        
        if a== t:
            return True

        return False
    
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        prevMap = {}  # val -> index

        for i, n in enumerate(nums):
            diff = target - n
            if diff in prevMap:
                return [prevMap[diff], i]
            prevMap[n] = i

            
class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        ga = [[]]
        setga = {}
        strs = ord(strs)
        strs =ins_sort(strs)
        strs = ord(strs)
        setga = {}
        for i in  range(len(strs)):
            a = []
            if i in a:
                a.add(ord(i).sort())        # need to solve
                
                
class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        a = {}
        c =[]
        for i in range(len(nums)):
            if nums[i] in a:
                a[nums[i]] +=1
            else:
                a[nums[i]] =1
        
        for i in a:
            if a[i].values > k:
                c.append(i)
        return c 
    
class Solution:

    def encode(self, strs: List[str]) -> str:
        for i in strs:
            for j in i:
                j = ord(j)
                j=j+1
                j= ord(j)
        return strs
                

    def decode(self, s: str) -> List[str]:
        for i in s:
            for j in i:
                j = ord(j)
                j=j-1
                j= ord(j)
                
        return s
    
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        # need to solve
    
class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        # need to solve

class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        # need to solve
        
class Solution:
    def isPalindrome(self, s: str) -> bool:
        l = []
        for i in s:
            if ord(26) < i < ord(48):
                l.append(i)
        le = 0
        r = len(l)-1
        for i in range((len(l)-1)/2):
            if l[le] == l[r]:
                le+=1
                r -=1
            else:
                return False 
        return True
    
    
class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        nums = ins_sort(nums)  
        lis = []
        for i in range(len(nums)/2 + 1):
            a= 0
            b = len(nums) -1
            if nums[a]+ nums[b] > target:
                b = b-1
            elif nums[a]+ nums[b] < target:
                a +=1
            else:
                lis.append(nums[a])
                lis.append(nums[b])
                return lis
        return None
    
class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        # Input: nums = [-1,0,1,2,-1,-4]

        # Output: [[-1,-1,2],[-1,0,1]]
        res = []
        nums.sort()
        for i in enumerate(nums):
            if a>0 and a==nums[i-1]:
                continue
            l,r = i+1 , len(nums) -1
            while l<r:
                sume = a + nums[l] + nums[r]
                if sume >0: 
                    r-=1
                elif sume <0:
                    l+=1
                else:
                    res.append([a,nums[l],nums[r]])
                    l+=1
                    while nums[l] == nums[l-1] and l<r:
                        l+=1
                        
        return res
    
        
class Solution:
    def maxArea(self, height: List[int]) -> int:
        maxa = 0
        l = 0
        r = len(height)
        for i in range((len(height)/2 +1)):
            maxb = max(height[l],height[r])
            if maxa < maxb:
                maxa = maxb
            b = min(height[l],height[r])
            if b == height[l]:
                l+=1
            else:
                r-=1
class Solution:
    def trap(self, height: List[int]) -> int:
        # need to do         
            
class Solution:
    def isValid(self, s: str) -> bool:
        Map = {")": "(", "]": "[", "}": "{"}
        stack = []
        for c in s:
            if c not in Map:
                stack.append(c)
                continue
            if not stack or stack[-1] != Map[c]:
                return False
            stack.pop()

        return not stack
    
class MinStack:
    def __init__(self):
        self.stack = []
        self.minStack = []

    def push(self, val: int) -> None:
        self.stack.append(val)
        val = min(val, self.minStack[-1] if self.minStack else val)
        self.minStack.append(val)

    def pop(self) -> None:
        self.stack.pop()
        self.minStack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.minStack[-1]
    
class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        stack = []
        for c in tokens:
            if c == "+":
                stack.append(stack.pop() + stack.pop())
            elif c == "-":
                a, b = stack.pop(), stack.pop()
                stack.append(b - a)
            elif c == "*":
                stack.append(stack.pop() * stack.pop())
            elif c == "/":
                a, b = stack.pop(), stack.pop()
            else:
                stack.append(int(c))
        return stack[0]
    
class Solution:
    def generateParenthesis(self, n: int) -> List[str]:    


class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        stac = []
        mapp =[]#value and index
        for i in range(len(temperatures)):
            if temperatures[i]<temperatures[i+1] and map == None:
                stac.append(1)
            elif temperatures[i]<temperatures[i+1]:
                stac.append()
                stackT, stackInd = map.pop()
                res[stackInd] = i - stackInd
                
            else:
                mapp.append([temperatures[i],i])
                
                #write above in proepr way 
                
class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        res = [0] * len(temperatures)
        stack = []  # pair: [temp, index]

        for i, t in enumerate(temperatures):
            while stack and t > stack[-1][0]:
                stackT, stackInd = stack.pop()
                res[stackInd] = i - stackInd
            stack.append((t, i))
        return res

class Solution:
    def carFleet(self, target: int, position: List[int], speed: List[int]) -> int:
        map = {}
        for i,j in zip(position,speed):
            map[i] = j
        map.sort()
        for i,j in map:
            a= i/j
            if 
                lis.append(a)
        a = 0
        co = 0
        for i in lis:
            if lis[i]<0:
                co +=1
        return co
    
class Solution:
    def carFleet(self, target: int, position: List[int], speed: List[int]) -> int:
        pair = [(p, s) for p, s in zip(position, speed)]
        pair.sort(reverse=True)
        stack = []
        for p, s in pair:  # Reverse Sorted Order
            stack.append((target - p) / s)
            if len(stack) >= 2 and stack[-1] <= stack[-2]:
                stack.pop()
        return len(stack)
 
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        maxa = 0
        l= 0
        r = len(heights)-1
            
        for i in range(len(heights)):
            are = o
            if are >maxa:
                maxa=are
            minpo = min(i,j)
            if minpo == i:
                i+=1
            else:
                j-=1 #this brutefore o(n^2)
                
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        maxArea = 0
        stack = []  # pair: (index, height)

        for i, h in enumerate(heights):
            start = i
            while stack and stack[-1][1] > h:
                index, height = stack.pop()
                maxArea = max(maxArea, height * (i - index))
                start = index
            stack.append((start, h))

        for i, h in stack:
            maxArea = max(maxArea, h * (len(heights) - i))
        return maxArea
#same as water problem but we have to take min vale and reject max

class Solution:
    def search(self, nums: List[int], target: int) -> int:
        tar = len(nums)/2
        while a==True:
            if nums[tar]<target:
                tar = (len(nums) - tar )/2
            elif nums[tar]>target:
                tar = (len(nums) - tar )/2
            else:
                a==True
 
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        l, r = 0, len(nums) - 1

        while l <= r:
            m = l + ((r - l) // 2)  # (l + r) // 2 can lead to overflow
            if nums[m] > target:
                r = m - 1
            elif nums[m] < target:
                l = m + 1
            else:
                return m
        return -1
    
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        f
        