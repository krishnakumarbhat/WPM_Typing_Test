class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        hset = set()
        for i in nums:
            if i in hset:
                return True
            else:
                hset.add(i)
                
        return False


class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        sh= {}
        th = {}
        
        for i in s:
            if i in sh:
                sh[i] +=1
            else:
                sh[i] =1

        for i in t:    
            if i in th:
                th[i] +=1
            else:
                th[i] =1
        if th == sh:
            return True
    return False    
        

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        
        
        
