# This version is using Linked allocation
# Name: Yusuf Fawzy Elnady           ID: 20160299


class File:
    def __init__(self, path, name, size):
        self.path = path
        self.size = size
        self.name = name
        self.allocatedblocks = []  # will contain lists of the indexes of the file


class Directory:
    def __init__(self, path='root/', name='root'):
        self.path = path
        self.name = name
        self.children = []


root = Directory()


class FSM:  # FreeSpaceManager
    DISK_SIZE = 20  # constant by KB
    Blocks = '01001001000000000000'
    nOfFreeBlocks = DISK_SIZE - 3

    @staticmethod
    def allocateLinked(size):  # Here I've to allocate spaces but which one?
        if size > FSM.nOfFreeBlocks: return []  # can't allocate
        flag = False
        startIdx = -1
        cnt = 0
        indices = []
        for i in range(FSM.DISK_SIZE):
            if FSM.Blocks[i] == '0':
                if flag == False:
                    startIdx = i
                    flag = True
                cnt += 1
                if cnt == size:
                    indices.append([startIdx, startIdx + cnt])
                    break
            else:
                # it means that the current char is 1, so add ones you have collected till now
                if flag == True:
                    indices.append([startIdx, startIdx + cnt])
                size -= cnt
                cnt = 0
                flag = False

        FSM.allocateSpace(indices)
        return indices

    @staticmethod
    def allocateSpace(indexes):
        print("Before {}".format(FSM.Blocks))
        for idx in indexes:
            start = idx[0]
            end = idx[1]
            size = end - start
            FSM.Blocks = FSM.Blocks[:start] + '1' * size + FSM.Blocks[end:]
        print("After  {}".format(FSM.Blocks))

    @staticmethod
    def deallocateSpace(indexes):
        print("Before {}".format(FSM.Blocks))

        for idx in indexes:
            start = int(idx[0])
            end = int(idx[1])
            size = end - start
            FSM.Blocks = FSM.Blocks[:start] + '0' * size + FSM.Blocks[end:]
        print("After  {}".format(FSM.Blocks))


class Linked:

    @staticmethod
    def createFolder(path):
        # function here to recursive then get me the last object if exist that will have the folder obj
        folders = path.split('/')
        name = folders[-1]
        newDir = Directory(path, name)
        res = Linked.searchDir(root, folders, 1,
                               len(folders) - 2)  # search in the tree till the before last directory (i-2)
        if res is not None:
            if Linked.searchInList(name, res.children, Directory) == -1:
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
                return Linked.searchDir(dir, folders, i + 1, n)
        return None

    @staticmethod
    def displayDiskStructure(node=root, n=0):
        print('  ' * n + '- <{}>'.format(node.name))
        if not node.children: return
        for folder in node.children:
            if isinstance(folder, Directory):
                Linked.displayDiskStructure(folder, n + 1)
            else:  # here so display the file
                print('  ' * (n + 1) + '- ' + folder.name + " : " + str(folder.allocatedblocks))

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
        parentDir = Linked.searchDir(root, folders, 1,
                                     len(folders) - 2)  # search in the tree till the 'last' directory (i-2)
        # now res contains the element before last that I need to delete one of its childern
        if parentDir is not None:
            idx = Linked.searchInList(name, parentDir.children, Directory)
            if idx != -1:
                dirTobeDeleted = parentDir.children[idx]
                Linked.deleteFolderRec(dirTobeDeleted)
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
                Linked.deleteFolderRec(folder)
                i += 1
            else:
                Linked.deleteFile(folder.path)  # all of our concern is to deleted the subfiles
            if cnt == n: break

    @staticmethod
    def deleteFile(path):
        folders = path.split('/')
        name = folders[-1]
        res = Linked.searchDir(root, folders, 1, len(folders) - 2)  # it means that this
        if res is not None:
            i = Linked.searchInList(name, res.children, File)
            if i == -1:
                print('There\'s no file with this name "{}"'.format(name))
            else:
                currentFile = res.children[i]
                FSM.nOfFreeBlocks += int(currentFile.size)

                # currently in i this is the index of the obj to be deleted found in res.children[i]
                print("The file to be deleted is '{}'".format(res.children[i].name))
                indexes = currentFile.allocatedblocks
                res.children.pop(i)
                FSM.deallocateSpace(indexes)
        else:
            print("Path doesn't exist")

    @staticmethod
    def createFile(path, size):  # where blocks is the ones to be edited
        folders = path.split('/')
        name = folders[-1]
        newFile = File(path, name, size)
        res = Linked.searchDir(root, folders, 1,
                               len(folders) - 2)  # search in the tree till the before last directory (i-2)
        if res is not None:  # if the file doesn't exist in the the children then you can add it
            if Linked.searchInList(name, res.children, File) == -1:
                indexes = FSM.allocateLinked(int(size))
                if not indexes:
                    print('No Available space')
                    return
                else:
                    res.children.append(newFile)
                    FSM.nOfFreeBlocks -= int(size)
                    # we also need to store which indexes are stored in the file
                    newFile.allocatedblocks = indexes
                    print('Allocated space is {}'.format(str(indexes)))
                    print('File "{}" is created Successfully'.format(newFile.name))
            else:
                print('File "{}" already exists'.format(name))
        else:
            print("Path doesn't exit")

    @staticmethod
    def storeFile(path, indexes, size):  # where blocks is the ones to be edited
        folders = path.split('/')
        name = folders[-1]
        newFile = File(path, name, size)
        print("size is " + size)
        res = Linked.searchDir(root, folders, 1,
                               len(folders) - 2)  # search in the tree till the before last directory (i-2)
        if res is not None:  # if the file doesn't exist in the the children then you can add it
            if Linked.searchInList(name, res.children, File) == -1:
                if not indexes:
                    print('No Available space')
                    return
                else:
                    res.children.append(newFile)
                    FSM.nOfFreeBlocks -= int(size)
                    # we also need to store which indexes are stored in the file
                    newFile.allocatedblocks = indexes
                    print('Allocated space is {}'.format(str(indexes)))
                    print('File "{}" is created Successfully'.format(newFile.name))
            else:
                print('File "{}" already exists'.format(name))
        else:
            print("Path doesn't exit")


def saveToFile():
    f = open('linked.vfs', 'w+')
    f.write('linked-')
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
        else:  # here so display the file
            f.write('F||{}||{}'.format(folder.path, folder.size))
            a = ''
            for idx in folder.allocatedblocks:
                a += '||' + str(idx[0]) + ',' + str(idx[1])
            a += '-'
            f.write(a)


def loadFromFile():  # Called at the start of the program
    try:
        f = open('linked.vfs', 'r+')
    except:
        return
    lines = f.read().split('-')
    print('ines is '+str(lines))
    FSM.Blocks = lines[1]
    FSM.DISK_SIZE = int(lines[2])
    FSM.nOfFreeBlocks = int(lines[3])

    for i in range(4, len(lines)):
        curr = lines[i].split("||")
        if curr[0] == "D":
            if curr[1] == 'root/':
                continue
            Linked.createFolder(curr[1])
        elif curr[0] == 'F':
            path = curr[1]
            size = curr[2]
            indexes = []
            for idx in range(3, len(curr)):
                c = curr[idx].split(',')
                start = c[0]
                end = c[1]
                indexes.append([start, end])  # I will store each indexes in this array,then I'll push them to storeFile
            # I have to iterate till I stop or what
            Linked.storeFile(path, indexes, size)


def execCommand(command):
    print('*' * 100)
    arr = command.split(' ')
    if 'CreateFile' in arr[0]:
        if (len(arr) < 3):
            print('Not Enough parameters')
        else:
            Linked.createFile(arr[1], arr[2])
    elif 'DisplayDiskStatus' in arr[0]:
        Linked.displayDiskStatus()
    elif 'DisplayDiskStructure' in arr[0]:
        Linked.displayDiskStructure()
    elif len(arr)<2:
        print('Not Enough Parameters')
    elif 'CreateFolder' in arr[0]:
        Linked.createFolder(arr[1])
    elif 'DeleteFile' in arr[0]:
        Linked.deleteFile(arr[1])
    elif 'DeleteFolder' in arr[0]:
        Linked.deleteFolder(arr[1])

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

    # execCommand('CreateFolder root/Folder1')
    # execCommand('CreateFile root/Folder1/file1.txt 2')
    #
    # execCommand('CreateFolder root/Folder2')
    # execCommand('CreateFile root/Folder2/file2.txt 2')
    # print(FSM.Blocks)
    # execCommand('CreateFile root/joe.txt 2')
    # execCommand('CreateFile root/Folder2/file3.txt 7')
    # execCommand('CreateFile root/Folder2/file6.txt 1')  # will say that I have no avail space here
    # execCommand('DisplayDiskStructure')
    #
    # execCommand('DisplayDiskStatus')
    #
    # execCommand('DeleteFolder root/Folder2')
    #
    # execCommand('DeleteFolder root')

    execCommand('DisplayDiskStructure')
    execCommand('DisplayDiskStatus')
    print(FSM.Blocks)

    saveToFile()

'''
linked-11111111110000000000-20-10-D||root/-D||root/Folder1-D||root/Folder2-F||root/Folder2/file2.txt||2||2,4-F||root/Folder2/file3.txt||7||0,2||4,9-F||root/Folder2/file4.txt||1||9,10-
'''
