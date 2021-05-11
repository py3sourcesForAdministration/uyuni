# uyu.py
program to handle "spacewalk", "SUSE Manager" or "uyuni" Patch and 
update management system on commandline.

Why another cli program to do this? Automatic handling of these systems is for
some things very unintuitive, sometimes really hard. 
For example: only uyuni, the latest fork has a builtin management for 
landscapes and staging of patches, but this is incredibly slow, creates lots 
of channels more than needed and is not nice to handle.
Also creating lists of patches for the next patchday, containing the CVEs
is more work than patching. Listing of Differences in channels is difficult.
...

I wrote this program to handle a special situation. I have to handle customers'
"SUSE Manager" systems over vpn and wan. No direct access. This makes CLI 
attractive.
Customers want only security patches to be applied in monthly intervals to
several landscapes. Managed systems are all salt based clients no traditional ones
and have different SUSE and Centos operating systems. 
Customers also want a reporting of patches and their CVEs to be applied to each 
system in advance. Customers also want to exclude patches that change certain software 
packages to an incompatible version.

I want all this to be done automatically. This program came to life. It had to be
flexible to serve multiple situations. All configuration regarding landscapes, 
staging and package exclusion is done in one configuration. See SRV.example
for detailed information. 

To get an idea how to plan the channel layout read the documents provided by SUSE
as "best practices for SUSE Manager". But keep in mind that their way creates
more channels than you really need.  

For everything else list the available modules of this program "uyu.py -l", 
issue "uyu.py --help", and before you really run a module
do "uyu.py -e Module help". 
Most modules are made for crontab use. Without additinal options they just do 
what the configuration file tells them and show no output. 

 
In the hope you will find it useful and it will make your work easier.  

Requirements:
    python >= 3.6,
    python modules (see uyu_imp.py),
    of course the nearby project pylibap 
  
Terms of use/License:

    uyu.py - program to handle "uyuni" patch and update management system 

    Copyright © 2020 Armin Poschmann

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

