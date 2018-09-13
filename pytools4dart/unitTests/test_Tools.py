import commands
import numpy as np

def compareBinaryFiles(filename1, filename2):
    cmd = 'cmp --verbose %s %s'%(filename1, filename2)
    status, output = commands.getstatusoutput(cmd) # python3 deprecated `commands` module FYI
    status = status if status < 255 else status%255
    if status > 1:
        raise RuntimeError('cmp returned with error (exitcode=%s, '
                'cmd=\"%s\", output=\n\"%s\n\")'%(status, cmd, output))
    elif status == 1:
        is_different = True
    elif status == 0:
        is_different = False
    else:
        raise RuntimeError('invalid exitcode detected')
    return is_different, output

# if __name__ == '__main__':
#     # create two binary files with different values
#     # file 1
#     tmp1 = np.arange(10, dtype=np.uint8)
#     tmp1.tofile('tmp1')
#     # file 2
#     tmp2 = np.arange(10, dtype=np.uint8)
#     tmp2[5] = 0xFF
#     tmp2.tofile('tmp2')
#     # compare using the shell command 'cmp'
#     is_different, output = run_cmp(filename1='tmp1', filename2='tmp2')
#     print 'is_different=%s, output=\n\"\n%s\n\"'%(is_different, output)