class Quanta:
    def __init__(self, parent, name, fieldname):
        self.parent = parent
        self.name = name
        self.fieldname = fieldname
        self.children = {}
        self.count = 0
        pass

    def __str__(self):
        return "<Quanta:field %s=%s, cnt=%s>"%(self.fieldname,self.name,self.count)

    def __repr__(self):
        return self.__str__()

    def add(self, flist):
        """
        "flist" stands for "Field List." It's been culled to be just us and our
        kids.
        """

        self.count += 1
        if len(flist) == 0:
            return
        if flist[0][1] not in self.children:
            self.children[flist[0][1]] = Quanta(self, flist[0][1], flist[0][0])
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

    def getQuanta(self, field=None):
        if field:
            qlist = []
            if self.fieldname == field:
                qlist.append(self)
            for c in self.children.values():
                qlist += c.getQuanta(field)
            return qlist
        pass

class CorrelationDB:
    def __init__(self, root_quanta):
        self.root = root_quanta

    def query2(self, field1, field2):
        """
        Gets the breakdown of field2 in relation to field1. e.g. field1
        is composed of so many <>, <>, and <> where <> comes from field2.
        """

        # Search for all field1 quanta
        f1_quanta = self.root.getQuanta(field=field1)
        #for q in f1_quanta:
        #    q.pprint()

        # Within each one, find all field2 quanta
        f2_quanta = []
        result = {}
        for q in f1_quanta:
            f2_quanta = q.getQuanta(field=field2)
            counts = {}
            for q2 in f2_quanta:
                if q2.name not in counts:
                    counts[q2.name] = 0
                counts[q2.name] += float(q2.count) / float(q.count)
                pass
            #print f2_quanta
            #print "%s: %s"%(q.name,str(counts))
            result[q.name] = counts

        return result

if __name__ == "__main__":
    indep_vars = ["asdf", "qwer", "zxcv"]
    dep_vars = ["tyui", "ghjk", "bnm"]
    f3_vars = ["a", "b", "c", "d"]

    import random
    objects = []
    for i in xrange(10000):
        objects.append({"f1": random.choice(indep_vars), "f2": random.choice(dep_vars), "f3": random.choice(f3_vars)})

    # work with quanta

    q = Quanta(None, "root", None)
    #for o in objects:
    #    q.add(cvtObjectToFieldList(o, "f1", "f2", "f3"))
    import cProfile
    cProfile.run("""q.addObj(objects, "f1", "f2", "f3") """)
    q.pprint()

    # Now test the correlationDB

    c = CorrelationDB(q)
    #print c.query2("f1", "f3")
    cProfile.run("""print c.query2("f1", "f3")""")

    cProfile.run("""print c.query2("f3", "f1")""")
