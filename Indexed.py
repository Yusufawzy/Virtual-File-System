# This version is using Indexed allocation
# Name: Yusuf Fawzy Elnady           ID: 20160299

class File:
    def __init__(self, path, name, size):
        self.path = path
        self.size = size
        self.name = name
        self.idxNode = None
        self.blocks = []


class Directory:
    def __init__(self, path='root/', name='root'):
        self.path = path
        self.name = name
        self.children = []


root = Directory()


class FSM:  # FreeSpaceManager
    DISK_SIZE = 20  # constant by KB
    Blocks = '0' * DISK_SIZE
    nOfFreeBlocks = DISK_SIZE

    @staticmethod
    def allocateIndexed(size):  # Here I've to allocate spaces but which one?
        if size + 1 > FSM.nOfFreeBlocks: return -1, []  # can't allocate
        cnt = 0
        idxNode = -1
        blocks = []
        for i in range(FSM.DISK_SIZE):
            if FSM.Blocks[i] == '0':
                idxNode = i
                FSM.Blocks = FSM.Blocks[:i] + '1' + FSM.Blocks[i + 1:]
                break
        for i in range(FSM.DISK_SIZE):
            if FSM.Blocks[i] == '0':
                FSM.Blocks = FSM.Blocks[:i] + '1' + FSM.Blocks[i + 1:]
                blocks.append(i)
                cnt += 1
            if cnt == size: break
        return idxNode, blocks

    @staticmethod
    def deallocateSpace(idxNode, blocks):
        print("Before {}".format(FSM.Blocks))
        FSM.Blocks = FSM.Blocks[:idxNode] + '0' + FSM.Blocks[idxNode + 1:]
        for idx in blocks:
            FSM.Blocks = FSM.Blocks[:idx] + '0' + FSM.Blocks[idx + 1:]
        print("After  {}".format(FSM.Blocks))


class Indexed:

    @staticmethod
    def createFolder(path):
        # function here to recursive then get me the last object if exist that will have the folder obj
        folders = path.split('/')
        name = folders[-1]
        newDir = Directory(path, name)
        res = Indexed.searchDir(root, folders, 1,
                                len(folders) - 2)  # search in the tree till the before last directory (i-2)
        if res is not None:
            if Indexed.searchInList(name, res.children, Directory) == -1:
                res.children.append(newDir)
                print('Directory "{}" is added Successfully'.format(name))
            else:
                print('Directory {} already exists'.format(name))
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
                return Indexed.searchDir(dir, folders, i + 1, n)
        return None

    @staticmethod
    def displayDiskStructure(node=root, n=0):
        print('  ' * n + '- <{}>'.format(node.name))
        if not node.children: return
        for folder in node.children:
            if isinstance(folder, Directory):
                Indexed.displayDiskStructure(folder, n + 1)
            else:  # here so display the file
                print('  ' * (n + 1) + '- {} : {} : {}'.format(folder.name, str(folder.idxNode), str(folder.blocks)))

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
        if (len(folders) < 2):
            print('Path is invalid');
            return
        parentDir = Indexed.searchDir(root, folders, 1,
                                      len(folders) - 2)  # search in the tree till the 'last' directory (i-2)
        # now res contains the element before last that I need to delete one of its childern
        if parentDir is not None:
            idx = Indexed.searchInList(name, parentDir.children, Directory)
            if idx != -1:
                dirTobeDeleted = parentDir.children[idx]
                Indexed.deleteFolderRec(dirTobeDeleted)
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
                Indexed.deleteFolderRec(folder)
                i += 1
            else:
                Indexed.deleteFile(folder.path)  # all of our concern is to deleted the subfiles
            if cnt == n: break

    @staticmethod
    def deleteFile(path):
        folders = path.split('/')
        name = folders[-1]
        res = Indexed.searchDir(root, folders, 1, len(folders) - 2)  # it means that this
        if res is not None:
            i = Indexed.searchInList(name, res.children, File)
            if i == -1:
                print('There\'s no file with this name "{}"'.format(name))
            else:
                currentFile = res.children[i]
                FSM.nOfFreeBlocks += int(currentFile.size) + 1  # cuz here we have the idx size is 1
                print("The file to be deleted is '{}'".format(res.children[i].name))
                blocks = currentFile.blocks
                idxNode = currentFile.idxNode
                res.children.pop(i)
                FSM.deallocateSpace(idxNode, blocks)
        else:
            print("Path doesn't exist")

    @staticmethod
    def createFile(path, size):  # where blocks is the ones to be edited
        folders = path.split('/')
        name = folders[-1]
        newFile = File(path, name, size)
        res = Indexed.searchDir(root, folders, 1,
                                len(folders) - 2)  # search in the tree till the before last directory (i-2)
        if res is not None:  # if the file doesn't exist in the the children then you can add it
            if Indexed.searchInList(name, res.children, File) == -1:
                idxNode, indexes = FSM.allocateIndexed(int(size))
                if not indexes:
                    print('No Available space')
                    return
                else:
                    res.children.append(newFile)
                    FSM.nOfFreeBlocks -= (int(size) + 1)
                    # we also need to store which indexes are stored in the file
                    newFile.blocks = indexes
                    newFile.idxNode = idxNode
                    print('IdxNode {} points to {}'.format(str(idxNode), str(indexes)))
                    print('File "{}" is created Successfully'.format(newFile.name))
            else:
                print('File "{}" already exists'.format(name))
        else:
            print("Path doesn't exit")

    @staticmethod
    def storeFile(path, blocks, size, idxNode):
        folders = path.split('/')
        name = folders[-1]
        newFile = File(path, name, size)
        res = Indexed.searchDir(root, folders, 1,
                                len(folders) - 2)  # search in the tree till the before last directory (i-2)
        if res is not None:  # if the file doesn't exist in the the children then you can add it
            if Indexed.searchInList(name, res.children, File) == -1:
                if not blocks:
                    print('No Available space')
                    return
                else:
                    res.children.append(newFile)
                    FSM.nOfFreeBlocks -= (size + 1)  # plus 1 cuz of idx node allocated
                    # we also need to store which indexes are stored in the file
                    newFile.blocks = blocks
                    newFile.idxNode = idxNode
                    # Now I've idxNode to be set as 1 and the blocks numbers to be also set to 1
                    FSM.Blocks = FSM.Blocks[:idxNode] + '1' + FSM.Blocks[idxNode + 1:]
                    for idx in blocks:
                        idx = int(idx)
                        FSM.Blocks = FSM.Blocks[:idx] + '1' + FSM.Blocks[idx + 1:]
                    print('IdxNode {} points to {}'.format(str(idxNode), str(blocks)))
                    print('File "{}" is created Successfully'.format(newFile.name))
            else:
                print('File "{}" already exists'.format(name))
        else:
            print("Path doesn't exit")


def saveToFile():
    f = open('indexed.vfs', 'w+')
    f.write('indexed-')
    f.write(FSM.Blocks + '-')
    f.write(str(FSM.DISK_SIZE) + '-')
    # cuz each time I use this variable as a new one, but actuially I do the calculations again so I gain an error
    f.write(str(FSM.DISK_SIZE) + '-')
    saveToFileRec(root, f)
    f.close()


def saveToFileRec(node, f):  # here I have ti add other info of the files .. how much it allocate
    f.write('D||' + node.path + '-')
    if not node.children: return
    for folder in node.children:
        if isinstance(folder, Directory):
            saveToFileRec(folder, f)
        else:
            # size||idxNode||blocksAllocated
            f.write('F||{}||{}||{}'.format(folder.path, folder.size, folder.idxNode))
            a = ''
            for idx in folder.blocks:
                a += '||' + str(idx)  # here am writing the children of idxNode to the file
            a += '-'
            f.write(a)


def loadFromFile():  # Called at the start of the program
    try:
        f = open('indexed.vfs', 'r+')
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
            Indexed.createFolder(curr[1])
        elif curr[0] == 'F':
            # F||root/Folder1/file1.txt||2||0||1||2-
            # size||idxNode||blocksAllocated
            path = curr[1]
            size = curr[2]
            idxNode = curr[3]
            blocks = []
            for idx in range(4, len(curr)):
                block = curr[idx]
                blocks.append(block)  # I will store each block the idxNode points to
            Indexed.storeFile(path, blocks, int(size), int(idxNode))


def execCommand(command):
    print('*' * 100)
    arr = command.split(' ')
    if 'CreateFile' in arr[0]:
        if (len(arr) < 3):
            print('Not Enough parameters')
        else:
            Indexed.createFile(arr[1], arr[2])

    elif 'DisplayDiskStatus' in arr[0]:
        Indexed.displayDiskStatus()
    elif 'DisplayDiskStructure' in arr[0]:
        Indexed.displayDiskStructure()
    elif len(arr) <2:
        print("Not Enough Parameters")
    elif 'CreateFolder' in arr[0]:
        Indexed.createFolder(arr[1])
    elif 'DeleteFile' in arr[0]:
        Indexed.deleteFile(arr[1])
    elif 'DeleteFolder' in arr[0]:
        Indexed.deleteFolder(arr[1])

    else:
        print('There\'s no such command')


def Input():
    while (True):
        a = input("Enter a command: ")
        if (a == 'Exit'): break
        execCommand(a)
        print('*' * 100)



def Start():
    loadFromFile()

    Input()

    #
    # execCommand('CreateFolder root/Folder1')
    # execCommand('CreateFile root/Folder1/file1.txt 2')
    #
    # execCommand('CreateFolder root/Folder2')
    # execCommand('CreateFile root/Folder2/file2.txt 2')
    # execCommand('CreateFile root/joe.txt 2')
    # execCommand('CreateFile root/Folder2/file3.txt 7')
    # execCommand('CreateFile root/Folder2/file6.txt 1')  # will say that I have no avail space here
    # execCommand('CreateFile root/Folder2/file7.txt 1')  # will say that I have no avail space here
    #
    # execCommand('DeleteFile root/joe.txt')
    # execCommand('DeleteFolder root')
    #
    # execCommand('DisplayDiskStructure')
    #execCommand('DisplayDiskStatus')

    print(FSM.Blocks)


    saveToFile()


'''
Indexed-11111111110000000000-20-10-D||root/-D||root/Folder1-D||root/Folder2-F||root/Folder2/file2.txt||2||2,4-F||root/Folder2/file3.txt||7||0,2||4,9-F||root/Folder2/file4.txt||1||9,10-
'''
