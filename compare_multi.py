import comparer

class tracked_list:
    """Ordered list with position tracking"""
    
    index = 0
    data = []

    def __init__(self, data):
        self.data = data

    def lookup(self, target):
        """Search list for an element equal to or larger than the target.

Update index as you search."""

        if len(self.data) == 0:
            return None

        # return?
        while self.data[self.index] < target:
            self.index += 1
            if self.index >= len(self.data):
                return None

        return self.data[self.index]

    def reset(self):
        self.index = 0

    def next(self):
        self.index += 1
        if self.index >= len(self.data):
            return None
        
        return self.data[self.index]
        
    

def compare_multi(lists):
    """Given tracked lists of users' friends and friend-ofs, return (a list of
usernames?) that follow/are followed by all given users."""
    # we assume the lists are in ascending order
    # - define the top, initializing it with the first element of the first
    #       list;
    # - while not end:
    #       - compare top with the current element of the next list;
    #       - if equal: continue;
    #       - if not equal: take the next element of the current list until
    #           the new one is equal or larger then the top; if larger, make
    #           it top, go back to the first list;
    #       - if we're at the last list already: a match has been found, record;

    # if the list is over while searching, comparison is finished

    top = lists[0].data[0]
    
    lists_num = len(lists)
    curr_list_idx = 0
    res = []
    
    while True:
        found = lists[curr_list_idx].lookup(top)

        if found == None:
            # not found, return ???
            return res
        
        if found == top:
            curr_list_idx += 1
        else:
            top = found
            curr_list_idx = 0

        if curr_list_idx == lists_num:
            res.append(top)
            curr_list_idx = 0
            top = lists[0].next()
            if top == None:
                return res


def comp_lj(usernames_list):
    """Given a string containing comma-separated list of usernames, find people
that follow/are followed by all given users."""

    usernames = map(str.strip, str(usernames_list).split(","))
    
    list_fs, list_fofs = [], []
    
    for un in usernames:
        friends, friend_ofs = comparer.get_friends(un)

        friends.sort()
        friend_ofs.sort()
        list_fs.append(tracked_list(friends))
        list_fofs.append(tracked_list(friend_ofs))

    return compare_multi(list_fs), compare_multi(list_fofs)
