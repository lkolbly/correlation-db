import copy

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
    def __init__(self, root_quanta=None, fieldlist=[]):
        self.root = root_quanta
        self.reverse_root = None
        self.fieldlist = fieldlist
        self.reverse_fieldlist = copy.deepcopy(fieldlist)
        self.reverse_fieldlist.reverse()

    def add(self, obj):
        if isinstance(obj, list):
            for o in obj:
                self.add(o)
            return

        if not self.root:
            self.root = Quanta(None, "root", None)
            self.reverse_root = Quanta(None, "root", None)

        self.root.addObj(obj, *self.fieldlist)
        self.reverse_root.addObj(obj, *self.reverse_fieldlist)

    def query2_rev(self, field1, field2):
        return self._query2(field1, field2, self.reverse_root)

    def query2(self, field1, field2):
        # Check to see if field2 comes before field1 in the fieldlist
        if self.fieldlist.index(field1) > self.fieldlist.index(field2):
            return self.query2_rev(field1, field2)
        return self._query2(field1, field2, self.root)

    #def query2(self, field1, field2):
    def _query2(self, field1, field2, root):
        """
        Gets the breakdown of field2 in relation to field1. e.g. field1
        is composed of so many <>, <>, and <> where <> comes from field2.
        """

        # Search for all field1 quanta
        f1_quanta = root.getQuanta(field=field1)
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

    def rootcause2(self, field, value):
        """
        Determine what values tend to be associated with the given field having
        the given value.

        Note that I only return single fields that have strong correlation, but
        I don't mine the data any further.
        """

        values = []
        for f in self.fieldlist:
            if f == field:
                continue
            corr = self.query2(field, f)
            new_values = []
            for k,v in corr[value].items():
                new_values.append((f, k, v))
                pass

            """
            # What would we expect if there were no correlation?
            # Note: This is also the mean. FYI
            expected = 1.0 / len(new_values)

            # Determine the standard deviation from that expected
            std_dev = 0.0
            for v in new_values:
                std_dev += v[2]
            std_dev = math.sqrt(std_dev / len(new_values))

            # Figure out who is
            """

            values += new_values
        print values
        return sorted(values, key=lambda v: v[2])
        return values

if __name__ == "__main__":
    apache_vars = ["1.0", "1.3", "1.5", "2.0", "2.2", "2.4"]
    php_vars = ["3.0", "4.0", "5.0"]
    bl_vars = ["malicious","safe"]
    bl_weighted_vars = ["malicious","malicious","malicious","safe"]

    import random
    objects = []
    for i in xrange(10000):
        apache = random.choice(apache_vars)
        php = random.choice(php_vars)
        if apache == "1.0":
            bl = random.choice(bl_weighted_vars)
        else:
            bl = random.choice(bl_vars)
        if random.randint(1,100) == 50:
            objects.append({"apache": apache, "bl": bl})
        else:
            objects.append({"apache": apache, "php": php, "bl": bl})

    # work with quanta

    q = Quanta(None, "root", None)
    #for o in objects:
    #    q.add(cvtObjectToFieldList(o, "f1", "f2", "f3"))
    import cProfile
    cProfile.run("""q.addObj(objects, "apache", "php", "bl") """)
    q.pprint()

    # Now test the correlationDB

    c = CorrelationDB(fieldlist=["apache", "php", "bl"])
    cProfile.run("""c.add(objects)""")

    #print c.query2("f1", "f3")
    cProfile.run("""print c.query2("apache", "bl")""")

    cProfile.run("""print c.query2_rev("bl", "apache")""")

    cProfile.run("""print c.query2("bl", "apache")""")

    cProfile.run("""print c.rootcause2("bl", "malicious")""")
