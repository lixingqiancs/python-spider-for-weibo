# python-spider-for-weibo

## usage

### example for request data

```bash
cd spider\ for\ python/weibo

sh spider.sh 
```

#### or
``` bash
cd spider\ for\ python/weibo

python weiboComments.py -h

python weiboComments.py -u 13xxxxxx767 -p ****** -m 2 -l "https://www.weibo.com/7293062537/ItJAm72t7?filter=hot&root_comment_id=0&type=comment" -t pc -o result_0329
```

### example for analysis data

``` bash
cd spider\ for\ python/weibo

python vis.py -h    

python vis.py -i pkl/comments_1585471431.pkl -o results 
```

#### or

``` bash
cd spider\ for\ python/

jupyter notebook
```

open the "Mycode.ipynb"
