import pandas as pd
from collections import defaultdict
import itertools
class TreeNode:
    def __init__(self,item,parent):
        self.item=item
        self.parent=parent
        self.child=[self]
        self.count=1
    def find_child(self,item): #根据物品名称寻找该节点对应的子节点，若没有则返回None
        for child in self.child:
            if child.item==item:
                return child
        return None
    def add_child(self,item): #根据物品名称添加子节点，如果物品对应的是自己的节点，则count加1。返回添加的节点类
        if item==self.item:
            self.count+=1
            return self
        node=TreeNode(item,self)
        self.child.append(node)
        return node
class FPTree:
    def __init__(self,items_list,threshold,total_transaction_num):
        self.threshold=threshold #支持度阈值
        self.total_transaction_num=total_transaction_num #初始的项集数量
        self.items_list=self.filter(items_list) #过滤支持度小于阈值的物品后的项集
        self.root=TreeNode('root',None) #设置根节点
        self.item_node=defaultdict(list) #该字典保存每个物品对应的节点TreeNode
        self.item_node[None].append(self.root)
        self.is_null=False #判断该树是不是空树（项集不为空）
        if self.items_list and list(itertools.chain.from_iterable(self.items_list)): #如果不是空树，开始遍历每个项集构建树
            for items in self.items_list:
                self.build_tree(items)
        else:
            self.is_null=True
        self.item2items=defaultdict(list) #该字典返回每个物品对应的关联物品列表
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
        items_list_flatten=list(itertools.chain.from_iterable(items_list)) #将二维项集展开为一维
        if not items_list_flatten:
            return None
        series=pd.Series(items_list_flatten).value_counts()
        con=series/self.total_transaction_num>=self.threshold
        series=series[con] #保留支持度大于阈值的物品集合
        for i,items in enumerate(items_list):
            items_list[i]=sorted(list(set(items)&set(series.index))) #进行本地过滤
        return items_list
    def insert_tree(self,items,parent_node:TreeNode):
        first=items[0]
        node=parent_node.find_child(first) 
        #再某节点上找到指定物品的子节点（也可能是父节点本身），
        #如果存在则返回节点，否则返回None
        if node:
            #如果节点存在，则次数加一
            node.count+=1
        else:
            #否则创建一个新的节点并且储存
            node=parent_node.add_child(first)
            self.item_node[first].append(node)
        if items[1:]:
            #将项集的第二个物品插入节点中，
            # 父节点为项集第一个物品对应的节点
            self.insert_tree(items[1:],node)
    def build_tree(self,items):
        first=items[0]
        for child in self.root.child:
            if child.item==first:
                self.insert_tree(items,child)
                return 
        self.insert_tree(items,self.root)
    def _get_item_relation(self,tree1,chain):
        #根据指定的物品生成条件树
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