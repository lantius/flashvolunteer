

Working in Eclipse. (this page is still in draft form)

### Installing Eclipse ###

An excellent guide for getting a basic Eclipse+Python install working is at http://urbansim.org/Download/ConfiguringEclipse. Make sure that you install the PyDev plugin.

I also recommend installing the [Aptana eclipse plugin](http://aptana.org/studio/download) for javascript and html code completion and syntax checking.


### Configuring Eclipse ###

Here are some misc notes on Eclipse use. These can be safely ignored.
  * If you want to use Visual Studio key mapping: F3 - go to definition, remap 'pydef goto definition' in windows::preferences::general::keys

### SVN integration ###

Here's how to use SVN within Eclipse.

#### Install subclipse or subversive ####

If you haven't already. They both do basically the same thing. I personally use subclipse.
  * [Subclipse](http://subclipse.tigris.org/)
  * [Subversive](http://www.eclipse.org/subversive/)

Note that you need to have an [svn client installed](Installation#Get_an_SVN_client.md) already.

#### Add the Flash Volunteer SVN repository ####

#### Checkout the FV repository as a project ####

#### Synchronizing your code ####

> make sure that in the synchronization view, you click on the button with the blue arrow
> that is the "incoming changes"
> the gray arrow going the other way is the "outgoing changes"
1:50 PM you also explicitly click "synchronize"
> it wont check the server automatically for incoming changes
> Aaron: ah that could be the prob
1:51 PM me: also, when you see something in red, that means there's a conflict
> Aaron: can I make it resolve comparisons automatically?
> me: or at least that you've locally modified a file that also has an incoming change
> > more or less
> > here's how
> > double click on a conflicting file
1:52 PM it will bring up a comparison editor
> > on the side of each file it shows what is happening
> > there are non-conflicting changes and conflicting changes
> > those appear as red
1:53 PM non-conflicting changes are blue or gray (depending on whether the addition/subtraction was an incoming or local modification)
> > in the upper right corner of the comparison editor, there are a set of buttons

> Aaron: yep
1:54 PM me: like "merge all non conflicting changes" and "merge current nonconflicting change
> > so my process is to look at what has changed
> > then determine if i can just do "merge all nonconflicting changes"
> > often that is all you need to do
> > if there are some red conflicts, you have go in and manually resolve

> Aaron: then save it locally?
1:55 PM me: you can edit the local version in the comparison editor
> > now, at this point, the file is still technically in conflict according to subclipse
> > (yes, locally)
> > so when you're done resolving the conflicts, you right click on the file that is red
1:56 PM and select the option that is like "conflicts merged" or something like that i dont remember

> Aaron: mark as merged


### Debugging in Eclipse ###

  * The debugger is good. See the documentation [here](http://pydev.org/manual_adv_debugger.html) for using the PyDev debugger.