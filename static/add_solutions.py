#!/usr/bin/env python3
"""
Script to add sample multi-language solutions to the database.
Run this script to populate the problem_solutions table with sample data.
"""

import sqlite3
import os

DB_PATH = "placement.db"

def add_sample_solutions():
    """Add sample solutions for coding problems"""
    
    if not os.path.exists(DB_PATH):
        print("Database not found. Please run the app first to initialize the database.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if problem_solutions table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='problem_solutions'
    """)
    
    if not cursor.fetchone():
        print("Creating problem_solutions table...")
        cursor.execute("""
        CREATE TABLE problem_solutions (
            id INTEGER PRIMARY KEY,
            problem_id INTEGER NOT NULL,
            language TEXT NOT NULL,
            code TEXT NOT NULL,
            time_complexity TEXT,
            space_complexity TEXT,
            explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (problem_id) REFERENCES coding_problems(id)
        )
        """)
    
    # Sample solutions for "Two Sum" problem (problem_id = 1)
    two_sum_solutions = [
        {
            'problem_id': 1,
            'language': 'Python',
            'code': '''def two_sum(nums, target):
    """
    Two Sum Solution using Hash Map
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    hash_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in hash_map:
            return [hash_map[complement], i]
        hash_map[num] = i
    return []

# Test
nums = [2, 7, 11, 15]
target = 9
print(two_sum(nums, target))  # Output: [0, 1]''',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(n)',
            'explanation': 'We use a hash map to store each number and its index. For each number, we check if its complement (target - number) exists in the hash map. If found, we return the indices.'
        },
        {
            'problem_id': 1,
            'language': 'C',
            'code': '''#include <stdio.h>

int* twoSum(int* nums, int numsSize, int target, int* returnSize) {
    int* result = (int*)malloc(2 * sizeof(int));
    *returnSize = 2;
    
    for (int i = 0; i < numsSize; i++) {
        for (int j = i + 1; j < numsSize; j++) {
            if (nums[i] + nums[j] == target) {
                result[0] = i;
                result[1] = j;
                return result;
            }
        }
    }
    return result;
}

int main() {
    int nums[] = {2, 7, 11, 15};
    int target = 9;
    int returnSize;
    int* result = twoSum(nums, 4, target, &returnSize);
    printf("[%d, %d]\\n", result[0], result[1]);
    return 0;
}''',
            'time_complexity': 'O(n²)',
            'space_complexity': 'O(1)',
            'explanation': 'Brute force approach: Check all pairs to find two numbers that add up to target. Simple but less efficient than hash map approach.'
        },
        {
            'problem_id': 1,
            'language': 'C++',
            'code': '''#include <iostream>
#include <vector>
#include <unordered_map>

using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int, int> map;
        for (int i = 0; i < nums.size(); i++) {
            int complement = target - nums[i];
            if (map.count(complement)) {
                return {map[complement], i};
            }
            map[nums[i]] = i;
        }
        return {};
    }
};''',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(n)',
            'explanation': 'Using unordered_map (hash map) for O(1) lookup. Iterate through the array once, checking if the complement exists in the map.'
        },
        {
            'problem_id': 1,
            'language': 'Java',
            'code': '''import java.util.*;

class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                return new int[] { map.get(complement), i };
            }
            map.put(nums[i], i);
        }
        throw new IllegalArgumentException("No two sum solution");
    }
}''',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(n)',
            'explanation': 'Using HashMap to store number-index pairs. For each element, check if its complement exists in the map.'
        },
        {
            'problem_id': 1,
            'language': 'JavaScript',
            'code': '''/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number[]}
 */
function twoSum(nums, target) {
    const map = new Map();
    for (let i = 0; i < nums.length; i++) {
        const complement = target - nums[i];
        if (map.has(complement)) {
            return [map.get(complement), i];
        }
        map.set(nums[i], i);
    }
    return [];
}

// Test
console.log(twoSum([2, 7, 11, 15], 9)); // [0, 1]''',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(n)',
            'explanation': 'Using JavaScript Map for efficient lookups. Iterate through array and check for complement.'
        },
        {
            'problem_id': 1,
            'language': 'Ruby',
            'code': '''# @param {Integer[]} nums
# @param {Integer} target
# @return {Integer[]}
def two_sum(nums, target)
  map = {}
  nums.each_with_index do |num, i|
    complement = target - num
    if map.key?(complement)
      return [map[complement], i]
    end
    map[num] = i
  end
  []
end

# Test
p two_sum([2, 7, 11, 15], 9)  # => [0, 1]''',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(n)',
            'explanation': 'Using Ruby hash for storing number-index pairs. Check for complement in hash.'
        },
        {
            'problem_id': 1,
            'language': 'Go',
            'code': '''package main

import "fmt"

func twoSum(nums []int, target int) []int {
    m := make(map[int]int)
    for i, num := range nums {
        complement := target - num
        if j, ok := m[complement]; ok {
            return []int{j, i}
        }
        m[num] = i
    }
    return []int{}
}

func main() {
    fmt.Println(twoSum([]int{2, 7, 11, 15}, 9)) // [0 1]
}''',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(n)',
            'explanation': 'Using Go map for O(1) lookups. Iterate once through the slice.'
        }
    ]
    
    # Sample solutions for "Palindrome Check" problem (problem_id = 2)
    palindrome_solutions = [
        {
            'problem_id': 2,
            'language': 'Python',
            'code': '''def is_palindrome(s):
    """
    Check if string is palindrome
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

# Test
print(is_palindrome("racecar"))  # True
print(is_palindrome("hello"))    # False''',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(1)',
            'explanation': 'Two-pointer approach: Compare characters from both ends moving towards the center.'
        },
        {
            'problem_id': 2,
            'language': 'Python',
            'code': '''def is_palindrome(s):
    # Alternative: Reverse string
    return s == s[::-1]

# Test
print(is_palindrome("racecar"))  # True''',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(n)',
            'explanation': 'Simple approach: Compare string with its reverse.'
        },
        {
            'problem_id': 2,
            'language': 'C',
            'code': '''#include <stdio.h>
#include <string.h>

int isPalindrome(char str[]) {
    int left = 0;
    int right = strlen(str) - 1;
    
    while (left < right) {
        if (str[left] != str[right]) {
            return 0;
        }
        left++;
        right--;
    }
    return 1;
}

int main() {
    char str[] = "racecar";
    printf("%d\\n", isPalindrome(str));  // 1
    return 0;
}''',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(1)',
            'explanation': 'Two-pointer technique in C.'
        }
    ]
    
    # Insert solutions
    all_solutions = two_sum_solutions + palindrome_solutions
    
    for sol in all_solutions:
        cursor.execute("""
            INSERT INTO problem_solutions 
            (problem_id, language, code, time_complexity, space_complexity, explanation)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            sol['problem_id'],
            sol['language'],
            sol['code'],
            sol['time_complexity'],
            sol['space_complexity'],
            sol['explanation']
        ))
    
    conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM problem_solutions")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ Successfully added {len(all_solutions)} sample solutions to the database!")
    print(f"Total solutions in database: {count}")

if __name__ == "__main__":
    add_sample_solutions()
