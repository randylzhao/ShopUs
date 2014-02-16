def format(unformated):
    nums = unformated[1:]
    one = "1-"
    if len(nums) < 10: return "1-111-111-1111"
    if len(nums) == 11:
    	nums = unformated[1:]
    first = nums[:3]
    second = nums[3:6]
    third = nums[6:10]
    return one + "-" + first + "-" + second + "-" + third

    
