from sklearn.base import TransformerMixin , BaseEstimator
import pandas as pd
import numpy as np


class stat_encoder(BaseEstimator, TransformerMixin):
 
  def __init__(self , cat_features   ):
    self.cat_features = cat_features
    self.map_encodes = {} 
    return None

  def fit(self, X=None, y=None):
     
    encoded_cols = pd.DataFrame()
    for COL in self.cat_features :

        s = pd.concat([ X[COL] , y] , axis =1)
        s_mean = s.groupby( by = [COL]).mean()
        s_50 = s.groupby( by = [COL]).median()
        s_25 = s.groupby( by = [COL]).quantile(0.25)
        s_75 = s.groupby( by = [COL]).quantile(0.75)
        s_min = s.groupby( by = [COL]).min()
        s_max = s.groupby( by = [COL]).max()

 

 
        
        self.map_encodes.update( {COL: {'_min': s_min.to_dict()['price'],
                                        '_max': s_max.to_dict()['price'],
                                        '_25': s_25.to_dict()['price'],
                                        '_50': s_50.to_dict()['price'],
                                        '_75': s_75.to_dict()['price'],
                                        '_mean': s_mean.to_dict()['price'],
                                       '_min_i': s['price'].max(),
                                        '_max_i': s['price'].max(),
                                        '_25_i': s['price'].quantile(0.25),
                                        '_50_i': s['price'].quantile(0.5),
                                        '_75_i': s['price'].quantile(0.75),
                                        '_mean_i': s['price'].mean() } })
    return self

  def transform(self, X=None):
    encoded_cols = pd.DataFrame()
    for COL in self.cat_features :

         

        enc_min = X[COL].map( self.map_encodes[COL]['_min'] )
        enc_max = X[COL].map(self.map_encodes[COL]['_max'] )
        enc_25 = X[COL].map(self.map_encodes[COL]['_25'] )
        enc_50 = X[COL].map(self.map_encodes[COL]['_50'] )
        enc_75 = X[COL].map(self.map_encodes[COL]['_75'] )
        enc_mean =  X[COL].map(self.map_encodes[COL]['_mean'] )
                     
        enc_min =  enc_min.fillna(self.map_encodes[COL]['_min_i']) 
        enc_max =  enc_max.fillna(self.map_encodes[COL]['_max_i'])  
        enc_25 =  enc_25.fillna(self.map_encodes[COL]['_25_i'])  
        enc_50 =  enc_50.fillna(self.map_encodes[COL]['_50_i'])  
        enc_75 =  enc_75.fillna(self.map_encodes[COL]['_75_i'])  
        enc_mean =  enc_mean.fillna(self.map_encodes[COL]['_mean_i'])                

        enc_min.name = COL + '_min'
        enc_max.name = COL + '_max'
        enc_25.name = COL + '_q25'
        enc_50.name = COL + '_q50'
        enc_75.name = COL + '_q75'
        enc_mean.name =  COL + '_mean' 

        encoded_cols = pd.concat([encoded_cols , enc_min, enc_25 ,enc_50 ,  enc_75 ,enc_max , enc_mean ] , axis =1)
        
     
    return pd.concat( [X.drop( self.cat_features , axis=1) , encoded_cols ] , axis =1  )


class stat_encoder2(BaseEstimator, TransformerMixin):
  """
 
  """
  def __init__(self , cat_features  , stat_enc , verbose = False ):
    self.cat_features = cat_features
    self.map_encodes = {} 
    self.stat_enc = stat_enc
    self.verbose = verbose
 
    return None

  def fit(self, X=None, y=None):

    def f_x(name):
        if name == 'mean':
            def F(x):
                return np.mean(x)

            return F
        if name == 'min':
            def F(x):
                return np.min(x)

            return F

        if name == 'max':
            def F(x):
                return np.max(x)

            return F
        if name[0] == 'q':
            def F(x):
                return x.quantile( q   =  float('0.'+  (name[1:]) ) )

            return F
    counter = 1
    N_ftr = len(self.cat_features)
    for COL in self.cat_features :
        if self.verbose == True:
          print('Preparing feature (',counter,'/',N_ftr,'): ', COL , sep='')
          counter += 1

        s = pd.concat([ X[COL] , y] , axis =1)
        if self.verbose == True:
          print( 'Вычислены статистики: ',end ='')
          
        f_dict = {}
        for Func in self.stat_enc:
            if self.verbose == True:
              print( Func,end =' ')
              
            s_f = s.groupby( by = [COL]).apply( func =   f_x(Func) )
            f_dict.update( {  '_'+Func  : s_f.to_dict()['price'] })
            f_dict.update({ '_'+Func +'_i' : f_x(Func)(s['price'] ) })

        self.map_encodes.update( {COL: f_dict  })
        if self.verbose == True:
          print(  )
    return self

  def transform(self, X=None):
 
    encoded_cols = pd.DataFrame()
    counter = 1
    N_ftr = len(self.cat_features)
    for COL in self.cat_features :
        if self.verbose == True:
          print('Preparing feature (',counter,'/',N_ftr,'): ', COL , sep='')
          counter += 1
        if self.verbose == True:
          print( 'Вычислены статистики: ',end ='')
        for Func in self.stat_enc:
            if self.verbose == True:
              print( Func,end =' ')
            
            enc_st = X[COL].map( self.map_encodes[COL]['_'+ Func ] )
            
            enc_st =  enc_st.fillna(self.map_encodes[COL]['_'+Func + '_i']) 
            
            enc_st.name =  COL + '_' + Func

            encoded_cols = pd.concat([encoded_cols , enc_st ], axis =1)
        if self.verbose == True:
            print(  )
 
        
     
    return pd.concat( [X.drop( self.cat_features , axis=1) , encoded_cols ] , axis =1  )
