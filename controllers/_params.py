import logging

class Parameters():
  
  def parameterize(req):
    params = {}
    for name in req.arguments():
      # TODO: if name = foo[1] then make a sub-hash of foos
      # accessed as params['foo'][1]

      
      params[name] = req.get_all(name)
      if len(params[name]) == 1: 
        params[name] = unicode(params[name][0])
    
    
#    params['name'] = req.get_all('name')[0] + '!'
    
    return params
    
  parameterize = staticmethod(parameterize)