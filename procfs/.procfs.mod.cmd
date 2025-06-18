savedcmd_/root/docu/reps/exercise/procfs/procfs.mod := printf '%s\n'   procfs.o | awk '!x[$$0]++ { print("/root/docu/reps/exercise/procfs/"$$0) }' > /root/docu/reps/exercise/procfs/procfs.mod
