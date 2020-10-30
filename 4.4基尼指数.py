import numpy as np
import pandas as pd
import copy
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams[u'font.sans-serif'] = ['simhei']
mpl.rcParams['axes.unicode_minus'] = False

dataset = pd.read_excel('D:\WaterMelon_2.0.xlsx', encoding='gbk')  # 读取数据
Attributes = dataset.columns[:-1]  # 所有属性的名称
# print(Attributes)
dataset = np.matrix(dataset)
dataset = dataset[:, :-1]
m, n = np.shape(dataset)  # 得到数据集大小
for i in range(m):  # 将标签替换成 好瓜 和 坏瓜
    if dataset[i, n - 1] == '是':
        dataset[i, n - 1] = '好瓜'
    else:
        dataset[i, n - 1] = '坏瓜'
attributeList = []  # 属性列表，每一个属性的取值，列表中元素是集合
for i in range(n):
    curSet = set()  # 使用集合是利用了集合里面元素不可重复的特性，从而提取出了每个属性的取值
    for j in range(m):
        curSet.add(dataset[j, i])
    attributeList.append(curSet)
# print(attributeList)
D = np.arange(0, m, 1)  # 表示每一个样本编号
A = list(np.ones(n))  # 表示每一个属性是否被使用，使用过了标为 -1
A[-1] = -1  # 将数据里面的标签和编号列标记为 -1
A[0] = -1


# print(A)
# print(D)


class Node(object):  # 创建一个类，用来表示节点的信息
    def __init__(self, title):
        self.title = title  # 上一级指向该节点的线上的标记文字
        self.v = 1  # 节点的信息标记
        self.children = []  # 节点的孩子列表
        self.deep = 0  # 节点深度
        self.ID = -1  # 节点编号


def isSameY(D):  # 判断所有样本是否属于同一类
    curY = dataset[D[0], n - 1]
    for i in range(1, len(D)):
        if dataset[D[i], n - 1] != curY:
            return False
    return True


def isBlankA(A):  # 判断 A 是否是空，是空则返回true
    for i in range(n):
        if A[i] > 0: return False
    return True


def isSameAinD(D, A):  # 判断在D中，是否所有的未使用过的样本属性均相同
    for i in range(n):
        if A[i] > 0:
            for j in range(1, len(D)):
                if not isSameValue(dataset[D[0], i], dataset[D[j], i]):
                    return False
    return True


def isSameValue(v1, v2):  # 判断v1、v2 是否相等
    return v1 == v2


def mostCommonY(D):  # 寻找D中样本数最多的类别
    res = dataset[D[0], n - 1]  # D中第一个样本标签
    maxC = 1
    count = {}
    count[res] = 1  # 该标签数量记为1
    for i in range(1, len(D)):
        curV = dataset[D[i], n - 1]  # 得到D中第i+1个样本的标签
        if curV not in count:  # 若之前不存在这个标签
            count[curV] = 1  # 则该标签数量记为1
        else:
            count[curV] += 1  # 否则 ，该标签对应的数量加一
        if count[curV] > maxC:  # maxC始终存贮最多标签对应的样本数量
            maxC = count[curV]  # res 存贮当前样本数最多的标签类型
            res = curV
    return res  # 返回的是样本数最多的标签的类型


def gini(D):  # 参数D中所存的样本的基尼值
    types = []  # 存贮类别标签
    count = {}  # 存贮每个类别对应的样本数量
    for i in range(len(D)):  # 统计D中存在的每个类型的样本数量
        curY = dataset[D[i], n - 1]
        if curY not in count:
            count[curY] = 1
            types.append(curY)
        else:
            count[curY] += 1
    ans = 1
    total = len(D)  # D中样本总数量
    for i in range(len(types)):  # 计算基尼值
        ans -= (count[types[i]] / total) ** 2
    return ans


def gini_indexD(D, p):  # 属性 p 上的基尼指数
    types = []
    count = {}
    for i in range(len(D)):  # 得到每一个属性取值上的样本编号
        a = dataset[D[i], p]
        if a not in count:
            count[a] = [D[i]]
            types.append(a)
        else:
            count[a].append(D[i])
    res = 0
    total = len(D)
    for i in range(len(types)):  # 计算出每一个属性取值分支上的基尼值，再计算出基尼指数
        res += len(count[types[i]]) / total * gini(count[types[i]])
    return res


def treeGenerate(D, A, title):
    node = Node(title)
    if isSameY(D):  # D中所有样本是否属于同一类
        node.v = dataset[D[0], n - 1]
        return node

    # 是否所有属性全部使用过  或者  D中所有样本的未使用的属性均相同
    if isBlankA(A) or isSameAinD(D, A):
        node.v = mostCommonY(D)  # 此时类别标记为样本数最多的类别（暗含可以处理存在异常样本的情况）
        return node  # 否则所有样本的类别应该一致

    gini_index = float('inf')
    p = 0
    for i in range(len(A)):  # 循环遍历A,找可以获得最小基尼指数的属性
        if (A[i] > 0):
            curGini_index = gini_indexD(D, i)
            if curGini_index < gini_index:
                p = i  # 存贮属性编号
                gini_index = curGini_index

    node.v = Attributes[p] + "=?"  # 节点信息
    curSet = attributeList[p]  # 该属性的所有取值
    for i in curSet:
        Dv = []
        for j in range(len(D)):  # 获得该属性取某一个值时对应的样本标号
            if dataset[D[j], p] == i:
                Dv.append(D[j])

            # 若该属性取值对应没有符合的样本，则将该分支作为叶子，类别是D中样本数最多的类别
            # 其实就是处理在没有对应的样本情况下的问题。那就取最大可能性的一类。
        if Dv == []:
            nextNode = Node(i)
            nextNode.v = mostCommonY(D)
            node.children.append(nextNode)
        else:  # 若存在对应的样本，则递归继续生成该节点下的子树
            newA = copy.deepcopy(A)  # 注意是深度复制，否则会改变A中的值
            newA[p] = -1
            node.children.append(treeGenerate(Dv, newA, i))
    return node


def countLeaf(root, deep):
    root.deep = deep
    res = 0
    if root.v == '好瓜' or root.v == '坏瓜':  # 说明此时已经是叶子节点了，所以直接返回
        res += 1
        return res, deep
    curdeep = deep  # 记录当前深度
    for i in root.children:  # 得到子树中的深度和叶子节点的个数
        a, b = countLeaf(i, deep + 1)
        res += a
        if b > curdeep: curdeep = b
    return res, curdeep


def giveLeafID(root, ID):  # 给叶子节点编号
    if root.v == '好瓜' or root.v == '坏瓜':
        root.ID = ID
        ID += 1
        return ID
    for i in root.children:
        ID = giveLeafID(i, ID)
    return ID


def plotNode(nodeTxt, centerPt, parentPt, nodeType):  # 绘制节点
    plt.annotate(nodeTxt, xy=parentPt, xycoords='axes fraction', xytext=centerPt,
                 textcoords='axes fraction', va="center", ha="center", bbox=nodeType,
                 arrowprops=arrow_args)


def dfsPlot(root):
    if root.ID == -1:  # 说明根节点不是叶子节点
        childrenPx = []
        meanPx = 0
        for i in root.children:
            cur = dfsPlot(i)
            meanPx += cur
            childrenPx.append(cur)
        meanPx = meanPx / len(root.children)
        c = 0
        for i in root.children:
            nodetype = leafNode
            if i.ID < 0: nodetype = decisionNode
            plotNode(i.v, (childrenPx[c], 0.9 - i.deep * 0.8 / deep), (meanPx, 0.9 - root.deep * 0.8 / deep), nodetype)
            plt.text((1.5 * childrenPx[c] + 0.5 * meanPx) / 2,
                     (0.9 - i.deep * 0.8 / deep + 0.9 - root.deep * 0.8 / deep) / 2, i.title)
            c += 1
        return meanPx
    else:
        return 0.1 + root.ID * 0.8 / (cnt - 1)


myDecisionTreeRoot = treeGenerate(D, A, "root")  # 生成决策树
cnt, deep = countLeaf(myDecisionTreeRoot, 0)  # 得到树的深度和叶子节点的个数
giveLeafID(myDecisionTreeRoot, 0)
# 绘制决策树
decisionNode = dict(boxstyle="sawtooth", fc="0.9", color='blue')
leafNode = dict(boxstyle="round4", fc="0.9", color='red')
arrow_args = dict(arrowstyle="<-", color='green')
fig = plt.figure(1, facecolor='white')
rootX = dfsPlot(myDecisionTreeRoot)
plotNode(myDecisionTreeRoot.v, (rootX, 0.9), (rootX, 0.9), decisionNode)
plt.show()