class CacheMemory:

    def __init__(self, cache_size, files_sizes):
        self.__memory = {}
        self.__memory_size = cache_size
        self.current_cache_size = 0
        self.files_sizes = files_sizes
        # initiate the memory randomly

    def replace_file(self):
        memory_list = []
        for id in self.__memory.keys():
            memory_list.append(self.__memory[id] + (id,))
        memory_list.sort(reverse=True)
        return memory_list[-1][2]

    def add_file_to_memory(self, file_id, file_size, time_counter):
        exist = False
        if file_id in self.__memory.keys():
            #  frequency, time to get in.
            self.__memory[file_id] = (self.__memory[file_id][0] + 1, time_counter)
            exist = True
        else:
            while (self.current_cache_size + file_size) >= self.__memory_size:
                to_del_file_id = self.replace_file()
                del self.__memory[to_del_file_id]
                self.current_cache_size -= self.files_sizes[to_del_file_id]
            self.__memory[file_id] = tuple()  # struct.Struct()
            self.__memory[file_id] = (1, time_counter)
            self.current_cache_size += file_size

        return exist
