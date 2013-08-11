class Quanta:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.children = {}
        self.count = 0
        pass

    def add(self, flist):
        """
        "flist" stands for "Field List." It's been culled to be just us and our
        kids.
        """

        self.count += 1
        if len(flist) == 0:
            return
        if flist[0][1] not in self.children:
            self.children[flist[0][1]] = Quanta(self, flist[0][1])
        self.children[flist[0][1]].add(flist[1:])
        pass

    def pprint(self, indent=0, rootcount=-1):
        for i in range(indent):
            print "  ",
        print "%s: Count %s"%(self.name, self.count),
        if self.parent:
            print " (%.2f%%)"%(100.0 * float(self.count) / float(self.parent.count)),

        if rootcount == -1:
            rootcount = self.count
        else:
            print " (%.2f%%)"%(100.0 * float(self.count) / float(rootcount)),

        print

        for c in self.children.values():
            c.pprint(indent=indent+1, rootcount=rootcount)
        pass

    def cvtObjectToFieldList(self, obj, *fields):
        flist = []
        for f in fields:
            if f not in obj:
                flist.append((f, None))
            else:
                flist.append((f, obj[f]))
        return flist

    def addObj(self, obj, *fields):
        if isinstance(obj, list):
            for o in obj:
                self.addObj(o, *fields)
            return
        self.add(self.cvtObjectToFieldList(obj, *fields))
        pass

class Index:
    """
    Maps a => b => c => d for a given number of these.
    Maintains the count for these relationships.
    """
    def __init__(self, *fields):
        self.counts = []
        self.fields = fields
        for f in fields:
            self.counts.append({})
        pass

    def add(self, obj):
        for i in xrange(len(self.counts)):
            pass
        pass

class CorrelationDB:
    def __init__(self):
        self.objects = []
        pass

    def add(self, obj):
        self.objects.append(obj)

    def _relate_object(self, index, obj, *fields):
        ind = index
        for f in fields:
            print f
            ref = ind[f]
        pass

    def relate(self, *fields):
        """
        Relate the given fields in a a => b => c => etc. fashion.
        """

        self._relate_object({}, self.objects[0], *fields)
        return None,None

        if len(fields) == 2:
            return relateTwoEnum(fields[0], fields[1])

        counts = []
        for i in xrange(len(fields)):
            counts.append({})

        for o in self.objects:
            for i in xrange(len(fields)):
                pass
            pass

    def relateTwoEnum(self, independant, dependant):
        """
        Related two fields in a x => y relation where x and y are both
        enum-able values.
        """

        indep_count = {}
        root_count = {}
        for o in self.objects:
            if o[independant] not in indep_count:
                indep_count[o[independant]] = {}
            if o[dependant] not in indep_count[o[independant]]:
                indep_count[o[independant]][o[dependant]] = 0
            indep_count[o[independant]][o[dependant]] += 1

            if o[independant] not in root_count:
                root_count[o[independant]] = 0
            root_count[o[independant]] += 1
        return indep_count, root_count

if __name__ == "__main__":
    c = CorrelationDB()

    indep_vars = ["asdf", "qwer", "zxcv"]
    dep_vars = ["tyui", "ghjk", "bnm"]
    f3_vars = ["a", "b", "c", "d"]

    import random
    objects = []
    for i in xrange(1000000):
        objects.append({"f1": random.choice(indep_vars), "f2": random.choice(dep_vars), "f3": random.choice(f3_vars)})

        """
    for o in objects:
        c.add(o)

    print "Building relation"
    t = c.relateTwoEnum("f1", "f2")
    from pprint import pprint
    pprint(t[0])
    pprint(t[1])

    t = c.relate("f1", "f2", "f3")
    pprint(t[0])
    pprint(t[1])
    """

    # work with quanta

    q = Quanta(None, "root")
    #for o in objects:
    #    q.add(cvtObjectToFieldList(o, "f1", "f2", "f3"))
    import cProfile
    cProfile.run("""q.addObj(objects, "f1", "f2", "f3") """)
    q.pprint()
