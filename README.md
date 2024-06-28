# Hydrowebnext utils

When Theia Hydroweb services passed from hydroweb old API to hydroweb.next, in March 2024, the way you can query for 
data has drastically, with breaking changes.

You can't query datasets by basin for instance, or even by station name (the stations are only queryable by 
their URN, which can't be deduced from the station name, or by a bounding polygon).

This was disruptive for several services relying on hydroweb data. This folder is intended to gather my utility scrips 
around hydroweb.next services.

