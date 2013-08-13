Quick Start
===========
First, a quick introduction into how this program thinks about the data it is presented with.

The purpose of this program is to ingest data and calculate statistics about said data. Specifically, the statistics we're calculating are correlation statistics. Data comes in the form of "objects", which within the API manifest themselves as Python dictionaries and when loaded from files manifest themselves as JSON objects.

Objects are made up of fields and values, which are respectively keys and values. Here's some example objects:
```
{"server": "Apache", "php": "5", "blacklist": true}
{"server": "Apache", "php": "5", "blacklist": false}
{"server": "NginX",  "php": "5", "blacklist": false}
{"server": "NginX",  "php": "4", "blacklist": true}
{"server": "Apache", "php": "4", "blacklist": true}
{"server": "Apache", "php": "4", "blacklist": true}
```

The centerpiece of this module is the CorrelationDB. Here's an example of how to create one, if the above objects are in file "data.json":
```
>>> c = correlationdb.CorrelationDB(fieldlist=["server", "php", "blacklist"])
>>> c.importFile("data.json")
```

Notice the "fieldlist" argument. The CorrelationDB needs to know what fields it is going to relate in the future, since it stores only the data required to correlate the data, and throws away the rest of the data. Because of this it can literally handle trillions of objects while using only megabytes of memory. It stores the breakdown of each field as a tree, in the order given by the fieldlist. For instance, the internal data structure of "c" after the above is:

```
>>> c.pprint()
server Apache: 4 (66%)
  php 5: 2 (50%) (33%)
    blacklist true: 1 (50%) (17%)
    blacklist false: 1 (50%) (17%)
  php 4: 2 (50%) (33%)
    blacklist true: 2 (100%) (33%)
server NginX: 2 (33%)
  php 5: 1 (50%) (17%)
    blacklist false: 1 (100%) (17%)
  php 4: 1 (50%) (17%)
    blacklist true: 1 (100%) (17%)
```

The meaning of this printout shouldn't affect you, but here it is in case it comes in handy:
<field> <value>: <# of objects> (<% of parent's objects>) (<% of all objects>)

Note the hierarchy. For instance, there is 1 object that has NginX and php 4 and is blacklisted.

But, back to the main point. The CorrelationDB presents an API to quickly and easily compare the relationship between any two fields:
```
>>> c.query2("server", "blacklist")
{"Apache": {"true": 0.75, "false": 0.25},
 "NginX":  {"true": 0.50, "false": 0.50}}
```

The above dictionary means that, for Apache servers, 75% of them are blacklisted while 25% are not. Meanwhile, for NginX servers, 50% are blacklisted while 50% are not.

The query could just as easily run the other way:
```
>>> c.query2("blacklist", "server")
{"true":  {"Apache": 0.75, "NginX": 0.25},
 "false": {"Apache": 0.50, "NginX": 0.50}}
```

Coincidentally, the numbers come out to be the same, but that's because the sample size is six. Note the meaning of this dictionary: Of all blacklisted servers, 75% are Apache and 25% are NginX.

To summarize:
- Of all Apache servers, 75% are blacklisted.
- Of all blacklisted servers, 75% are Apache.
The numbers are the same in this example, but it is important that you recognize the difference.

Now, you ask, "What about more complex queries? What if I wanted to ask 'What tends to cause blacklisted sites?'"

Yes, I am acutely aware that correlation does not equal causation. However, when it comes to big data it is my firm belief that strong correlation is an indicator of a related cause, if not direct causation.

Which is why I say "tends to cause" and not "causes". If it bothers you, do a find-replace on this document and replace "tends to cause" with "strongly indicates a relation that may or may not be indicative of a cause"

But, your question may be: "What tends to cause blacklisted sites?" CorrelationDB has a function called "rootcause2" that will answer that question:
```
>>> c.rootcause2("blacklist", "true")
[("php",    "5",      1, 0.33),
 ("server", "NginX",  1, 0.5),
 ("server", "Apache", 3, 0.75),
 ("php",    "4",      3, 1.00)]
```

The first argument is the field, the second argument is the value you're trying to find a cause for.

rootcause returns a sorted list of tuples. Here's what the values of the tuples mean, in order:
1. Field name (e.g. "php")
2. Field value (e.g. "5")
3. Number of matching objects with the given field/value pair (e.g. 1 object had both php: 5 and blacklist: true)
4. Percentage of all matching objects that had the given field/value pair (e.g. 33% of all php:5 objects had blacklist:true)

Looking at the results above, we can safely conclude:
- php 4 is blacklisted 100% of the time.
- Apache is blacklisted more often than not (75% of the time).
- NginX is a 50/50 tossup.
- and php 5 is blacklisted less than half the time.

Somebody who was analyzing the data could look at this and say "Well, it look like PHP 4 is often blacklisted. I will start looking there."

Planned Future Features:
========================
Improve rootcause, to handle combinations of fields in the correlations:
Given data:
```
{"server": "Apache", "php": "5", "blacklist": true}
{"server": "Apache", "php": "5", "blacklist": false}
{"server": "NginX",  "php": "5", "blacklist": false}
{"server": "NginX",  "php": "4", "blacklist": false} # This is the only difference from above
{"server": "Apache", "php": "4", "blacklist": true}
{"server": "Apache", "php": "4", "blacklist": true}
```

```
>>> c.rootcause2("blacklist", "true")
[("server", "NginX",  0, 0.00),
 ("php",    "5",      1, 0.33),
 ("php",    "4",      2, 0.66),
 ("server", "Apache", 3, 0.75)] # This is the existing functionality.

>>> c.rootcause("blacklist=true")
(server=NginX, 0%)
(php=5, 33%)
(server=Apache, php=5, 50%)
(php=4, 66%)
(server=Apache, 75%)
(server=Apache, php=4, 100%) # Identifies that all Apache/4 servers are blacklisted.
```

Handle nested dictionaries and lists as objects:
```
{"server": {"type": "Apache", "version": [2, 2, 22]},
 "blacklist": ["EmergingThreats", "SpamHaus"]}
```

Handle "fuzzy" queries:
```
>>> c.rootcause("blacklist=true", fuzzy="server.version <= server.version[0]")
# Instead of using [2,2,22] as the server version uses simply "2". Ideally would be able to handle string regex replacing as well: "server.type <= r/Apache.*/Apache/" would change server.type="Apache 2.4.0e" to "Apache"
```

Until Later,
Lane

