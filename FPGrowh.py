import pandas as pd
from collections import defaultdict
import itertools
class TreeNode:
    def __init__(self,item,parent):
        self.item=item
        self.parent=parent
        self.child=[self]
        self.count=1
    def find_child(self,item): #Search for the corresponding child nodes of the node based on the item name, and return None if none are available
        for child in self.child:
            if child.item==item:
                return child
        return None
    def add_child(self,item): #Add child nodes based on the item name. 
        #If the item corresponds to your own node, add 1 to the count. Return the added node class
        if item==self.item:
            self.count+=1
            return self
        node=TreeNode(item,self)
        self.child.append(node)
        return node
class FPTree:
    def __init__(self,items_list,threshold,total_transaction_num):
        self.threshold=threshold #Support threshold
        self.total_transaction_num=total_transaction_num #Initial number of itemsets
        self.items_list=self.filter(items_list) #The itemset after filtering items with support below the threshold
        self.root=TreeNode('root',None) #Set root node
        self.item_node=defaultdict(list) #This dictionary stores the TreeNode corresponding to each item
        self.item_node[None].append(self.root)
        self.is_null=False #Determine if the tree is an empty tree (the itemset is not empty)
        if self.items_list and list(itertools.chain.from_iterable(self.items_list)): #If it's not an empty tree, start traversing each itemset to construct a tree
            for items in self.items_list:
                self.build_tree(items)
        else:
            self.is_null=True
        self.item2items=defaultdict(list) #This dictionary returns a list of associated items for each item
    def get_path(self,node:TreeNode): 
        items_list_path,nums=[],node.count
        while node is not self.root:
            node=node.parent
            items_list_path.append(node.item)
        items_list_path.remove('root')
        if items_list_path:
            return [items_list_path for _ in range(nums)]
    def get_items_due_path(self,item):
        res=[]
        for node in self.item_node[item]:
            p=self.get_path(node)
            if p:
                res.extend(p)
        return res
    def filter(self,items_list:list[list[str]]):
        items_list_flatten=list(itertools.chain.from_iterable(items_list)) #Expand the two-dimensional itemset into one dimension
        if not items_list_flatten:
            return None
        series=pd.Series(items_list_flatten).value_counts()
        con=series/self.total_transaction_num>=self.threshold
        series=series[con] #Retain the collection of items with support greater than the threshold
        for i,items in enumerate(items_list):
            items_list[i]=sorted(list(set(items)&set(series.index))) #Perform local filtering
        return items_list
    def insert_tree(self,items,parent_node:TreeNode):
        first=items[0]
        node=parent_node.find_child(first) 
        #Find the child node (or possibly the parent node itself) of the specified item on a certain node,
        #If it exists, return the node; otherwise, return None
        if node:
            node.count+=1
        else:
            #Otherwise, create a new node and store it
            node=parent_node.add_child(first)
            self.item_node[first].append(node)
        if items[1:]:
            #Insert the second item from the itemset into the node,
            #The parent node is the node corresponding to the first item in the itemset
            self.insert_tree(items[1:],node)
    def build_tree(self,items):
        first=items[0]
        for child in self.root.child:
            if child.item==first:
                self.insert_tree(items,child)
                return 
        self.insert_tree(items,self.root)
    def _get_item_relation(self,tree1,chain):
        #Generate condition tree based on specified items
        tree2=FPTree(tree1.get_items_due_path(chain[-1]),self.threshold,self.total_transaction_num)
        if tree2.is_null:
            return 
        self.item_list=list(set(itertools.chain.from_iterable(tree2.items_list)))
        for item in self.item_list:
            self.item2items[chain[0]].append(tuple(chain+[item]))
            self._get_item_relation(tree2,chain+[item])
    def get_item_relation(self,taregt_item):
        self._get_item_relation(self,[taregt_item])
    def get_all_item_relation(self):
        for item in set(itertools.chain.from_iterable(self.items_list)):
            self.get_item_relation(item)
if __name__=='__main__':
    transaction=[['A','B','F'],['B','C','D'],['A','C','D','E'],['A','D','E'],['A','B','C','H'],['A','B','C','D'],
             ['A'],['A','B','C','G'],['A','B','D'],['B','C','E']]
    tree=FPTree(transaction,0.2,10)
    tree.get_all_item_relation()
    print(tree.item2items)
## defaultdict(list,
##    {'B': [('B', 'A')],
##     'C': [('C', 'A'), ('C', 'B'), ('C', 'B', 'A')],
##     'D': [('D', 'C'),
##      ('D', 'C', 'A'),
##      ('D', 'C', 'B'),
##      ('D', 'A'),
##      ('D', 'B'),
##      ('D', 'B', 'A')],
##     'E': [('E', 'C'), ('E', 'A'), ('E', 'D'), ('E', 'D', 'A')]})
