# This version is using contiguous allocation
# Name: Yusuf Fawzy Elnady           ID: 20160299

class File:
    def __init__(self, path, name, size):
        self.path = path
        self.size = size
        self.name = name
        self.allocatedblocks = []


class Directory:
    def __init__(self, path='root/', name='root'):
        self.path = path
        self.name = name
        self.children = []


root = Directory()


class FSM:  # FreeSpaceManager
    DISK_SIZE = 30  # constant by KB
    Blocks = '0' * DISK_SIZE
    nOfFreeBlocks = DISK_SIZE

    @staticmethod
    def allocateCtgs(size):
        # I need a way to allocate spaces in the worst case
        # search till the end, when reach 1 then means there's a new block is coming, what's the block of the current
        # Is the size greater than the previous size
        if size > FSM.nOfFreeBlocks: return -1  # can't allocate
        biggestSize = 0
        biggestIdx = -1
        flag = False
        startIdx = -1
        cnt = 0

        for i in range(FSM.DISK_SIZE):
            if FSM.Blocks[i] == '0':
                if flag == False:
                    startIdx = i
                    flag = True
                cnt += 1
            else:
                if (cnt >= size and cnt >= biggestSize):
                    biggestIdx = startIdx
                    biggestSize = cnt
                cnt = 0
                flag = False
        if (cnt >= size and cnt >= biggestSize):
            biggestIdx = startIdx
            biggestSize = cnt

        FSM.allocateSpace(biggestIdx, biggestIdx + size, size)

        print("biggest idx is {}".format(biggestIdx))
        return biggestIdx

    @staticmethod
    def allocateSpace(start, end, size):  # Here I've to allocate spaces but which one?
        print("Before {}".format(FSM.Blocks))
        if (start == -1): return
        FSM.Blocks = FSM.Blocks[:start] + '1' * size + FSM.Blocks[end:]
        print("After  {}".format(FSM.Blocks))

    @staticmethod
    def deallocateSpace(start, end, size):
        FSM.nOfFreeBlocks += int(size)
        print("Before {}".format(FSM.Blocks))
        FSM.Blocks = FSM.Blocks[:start] + '0' * size + FSM.Blocks[end:]
        print("After  {}".format(FSM.Blocks))


class Ctgs:

    @staticmethod
    def createFolder(path):
        # function here to recursive then get me the last object if exist that will have the folder obj
        folders = path.split('/')
        name = folders[-1]
        newDir = Directory(path, name)
        res = Ctgs.searchDir(root, folders, 1,
                             len(folders) - 2)  # search in the tree till the before last directory (i-2)
        if res is not None:
            if Ctgs.searchInList(name, res.children, Directory) == -1:
                res.children.append(newDir)
                print('Directory "{}" is added Successfully'.format(name))
            else:
                print('Directory {} already exists'.format(name))
        else:
            print("Path doesn't exit")

    @staticmethod
    def deleteFile(path):
        folders = path.split('/')
        name = folders[-1]
        res = Ctgs.searchDir(root, folders, 1, len(folders) - 2)  # it means that this
        if res is not None:
            i = Ctgs.searchInList(name, res.children, File)
            if i == -1:
                print('There\'s no file with this name "{}"'.format(name))
            else:
                currentFile = res.children[i]
                # currently in i this is the index of the obj to be deleted found in res.children[i]
                print("The file to be deleted is '{}'".format(res.children[i].name))
                toBeFreed = currentFile.allocatedblocks
                res.children.pop(i)
                FSM.deallocateSpace(toBeFreed[0][0], toBeFreed[0][1], int(currentFile.size))
        else:
            print("Path doesn't exist")

    @staticmethod
    def createFile(path, size):  # where blocks is the ones to be edited
        folders = path.split('/')
        name = folders[-1]
        newFile = File(path, name, size)
        res = Ctgs.searchDir(root, folders, 1,
                             len(folders) - 2)  # search in the tree till the before last directory (i-2)
        if res is not None:  # if the file doesn't exist in the the children then you can add it
            if Ctgs.searchInList(name, res.children, File) == -1:
                start = FSM.allocateCtgs(int(size))
                if (start == -1):
                    print('No Available space')
                    return
                else:
                    res.children.append(newFile)
                    FSM.nOfFreeBlocks -= int(size)
                    # we also need to store which indexes are stored in the file
                    newFile.allocatedblocks.append([start, start + int(size)])
                    print('Allocated space is from {} to {}'.format(newFile.allocatedblocks[0][0]
                                                                    , newFile.allocatedblocks[0][1]))
                    print('File "{}" is created Successfully'.format(newFile.name))
            else:
                print('File "{}" already exists'.format(name))
        else:
            print("Path doesn't exit")

    @staticmethod
    def storeFile(path, start, end):  # where blocks is the ones to be edited
        folders = path.split('/')
        name = folders[-1]
        size = int(end) - int(start)
        newFile = File(path, name, size)
        res = Ctgs.searchDir(root, folders, 1,
                             len(folders) - 2)  # search in the tree till the before last directory (i-2)
        if res is not None:  # if the file doesn't exist in the the children then you can add it
            if Ctgs.searchInList(name, res.children, File) == -1:
                res.children.append(newFile)
                FSM.nOfFreeBlocks -= (size)
                # we also need to store which indexes are stored in the file
                newFile.allocatedblocks.append([start, end])
                print('Allocated space is from {} to {}'.format(newFile.allocatedblocks[0][0]
                                                                , newFile.allocatedblocks[0][1]))
                print('File "{}" is created Successfully'.format(newFile.name))
            else:
                print('File "{}" already exists'.format(name))
        else:
            print("Path doesn't exit")

    @staticmethod
    def searchInList(name, arr, obj):
        for i, file in enumerate(arr):
            if file.name == name and isinstance(file, obj):
                return i
        return -1

    @staticmethod
    def searchDir(node, folders, i, n):
        if len(folders) == 2 and isinstance(node, Directory): return node
        for dir in node.children:
            if folders[i] == dir.name and isinstance(dir, Directory):
                if i == n and folders[n] == dir.name: return dir
                return Ctgs.searchDir(dir, folders, i + 1, n)
        return None

    @staticmethod
    def displayDiskStructure(node=root, n=0):
        print('  ' * n + '- <{}>'.format(node.name))
        if not node.children: return
        for folder in node.children:
            if isinstance(folder, Directory):
                Ctgs.displayDiskStructure(folder, n + 1)
            else:  # here so display the file
                print('  ' * (n + 1) + '- ' + folder.name)

    @staticmethod
    def displayDiskStatus():
        print('Total Allocated space is {}'.format(FSM.DISK_SIZE - FSM.nOfFreeBlocks))
        print('Total Available space is {}'.format(FSM.nOfFreeBlocks))
        allocated = [];
        free = []
        for i, c in enumerate(FSM.Blocks):
            if (c == '0'):
                free.append(i)
            else:
                allocated.append(i)
        print('Allocated blocks are ' + str(allocated))
        print('Free blocks are ' + str(free))

    @staticmethod
    def deleteFolder(path):
        folders = path.split('/')
        name = folders[-1]
        if (name == 'root'): print("Root can't be deleted");return
        if (len(folders) <2):
            print('Path is invalid') ;return
        parentDir = Ctgs.searchDir(root, folders, 1,
                                   len(folders) - 2)  # search in the tree till the 'last' directory (i-2)
        # now res contains the element before last that I need to delete one of its childern

        if parentDir is not None:
            idx = Ctgs.searchInList(name, parentDir.children, Directory)
            if idx != -1:
                dirTobeDeleted = parentDir.children[idx]
                Ctgs.deleteFolderRec(dirTobeDeleted)
                parentDir.children.pop(idx)
                # I need to go back step then delete this folder from this directory
                print('Directory "{}" is deleted Successfully'.format(name))
            else:
                print("Path doesn't exit")

    @staticmethod
    def deleteFolderRec(node):
        if not node.children: return
        i = cnt = 0
        n = len(node.children)
        # problem was when deleting an object then returning to delete others I have to change the idx
        while (True):
            cnt += 1
            folder = node.children[i]
            if isinstance(folder, Directory):
                Ctgs.deleteFolderRec(folder)
                i += 1
            else:
                Ctgs.deleteFile(folder.path)  # all of our concern is to deleted the subfiles
            if cnt == n: break


def saveToFile():
    f = open('ctgs.vfs', 'w+')
    f.write('Ctgs-')
    f.write(FSM.Blocks + '-')
    f.write(str(FSM.DISK_SIZE) + '-')
    f.write(str(FSM.DISK_SIZE) + '-')
    saveToFileRec(root, f)
    f.close()


def saveToFileRec(node, f):  # here I have ti add other info of the files .. how much it allocate
    f.write('D||' + node.path + '-')
    if not node.children: return
    for folder in node.children:
        if isinstance(folder, Directory):
            saveToFileRec(folder, f)
        else:  # here so display the file
            f.write('F||{}||{}||{}-'.format(folder.path, folder.allocatedblocks[0][0], folder.allocatedblocks[0][1]))


def loadFromFile():  # Called at the start of the program
    try:

        f = open('ctgs.vfs', 'r+')
    except:
        return
    lines = f.read().split('-')
    FSM.Blocks = lines[1]
    FSM.DISK_SIZE = int(lines[2])
    FSM.nOfFreeBlocks = int(lines[3])

    for i in range(4, len(lines)):
        curr = lines[i].split("||")
        if curr[0] == "D":
            if curr[1] == 'root/':
                continue
            Ctgs.createFolder(curr[1])
        elif curr[0] == 'F':
            path = curr[1]
            start = curr[2]
            end = curr[3]
            Ctgs.storeFile(path, int(start), int(end))


def execCommand(command):
    print('*' * 100)
    arr = command.split(' ')
    if 'CreateFile' in arr[0]:
        if(len(arr)<3): print('Not Enough parameters')
        else :Ctgs.createFile(arr[1], arr[2])
    elif 'DisplayDiskStatus' in arr[0]:
        Ctgs.displayDiskStatus()
    elif 'DisplayDiskStructure' in arr[0]:
        Ctgs.displayDiskStructure()
    elif len(arr)<2:
        print('Not Enough Parameters')
    elif 'CreateFolder' in arr[0]:
        Ctgs.createFolder(arr[1])
    elif 'DeleteFile' in arr[0]:
        Ctgs.deleteFile(arr[1])
    elif 'DeleteFolder' in arr[0]:
        Ctgs.deleteFolder(arr[1])
    else:
        print('There\'s no such command')


def Input():
    while (True):
        a = input("Enter a command: ")
        if (a=='Exit'):break
        execCommand(a)
        print('*' * 100)

def Start():
    loadFromFile()
    Input()
    #
    # execCommand('CreateFolder root/Folder1')
    # execCommand('CreateFile root/Folder1/file1.txt 5')
    #
    # execCommand('CreateFolder root/Folder2')
    # execCommand('CreateFile root/Folder2/file2.txt 5')
    # execCommand('CreateFile root/Folder2/file4.txt 2')
    #
    # execCommand('CreateFile root/Folder2/file3.txt 2')
    # execCommand('CreateFile root/Folder2/file5.txt 1')
    #
    #
    # execCommand('CreateFile root/Folder1/file3.txt 21')
    # execCommand('DisplayDiskStatus')
    #
    # execCommand('DisplayDiskStructure')

    saveToFile()

    execCommand('DisplayDiskStatus')

    execCommand('DisplayDiskStructure')
    print(FSM.Blocks)


'''
Ctgs-111110000000000000000000000000-30-25-D||root/-D||root/folder1-F||root/folder1/joe.txt||0||5-D||root/folder3-
'''
