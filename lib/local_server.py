import webuiapi
from PIL import Image



def draw_pic():
    # 参数与官方文档的txt2img完全一致，参照上文参数文档
    result = api.txt2img(
        prompt="a yong girl,upper_body,profile,close-up,macro_shot,",
        seed=-1,
    )

    # save image with jpg format
    img = result.image
    img.save("output2.jpg", quality=90)

# create API client with custom host, port
api = webuiapi.WebUIApi(host='www.xuhuanju.com', port=8060)
options = {}
options['sd_model_checkpoint'] = 'majicmixRealistic_v7.safetensors [7c819b6d13]'
api.set_options(options)
models = api.get_sd_models()
print(models)
draw_pic()
