import os
import sys
sys.path.append(os.path.abspath('../ohdevtools'))
sys.path.append(os.path.abspath('ohdevtools'))
import JenkinsBuildUtils as build
import shutil


class Runner():
    output_dir = "build/packages"
    build_dir  = "build"

    def __init__(self, nuget_api_key, ohnet_version, ohnet_generated_version, release_version, publish_release):
        self.release_version         = release_version

        print('Fetching dependencies...')
         # write release version in dependencies.json
        f1 = open('projectdata/dependencies.json', 'r')
        c  = f1.read() % {'ohnet_version' : ohnet_version, 'ohnet_generated_version' : ohnet_generated_version}
        f1.close()
        
        f2 = open('projectdata/dependencies.json', 'w')
        f2.write(c)
        f2.close()

        print('Running go fetch...')
        build.fetch('--clean --all')

        print('Packaging...')
        self.pack_nuget('src/ohNet.nuspec')
        self.pack_nuget('src/ohNet.NET.nuspec')
        self.pack_nuget('src/ohNetGeneratedProxies.Combined.nuspec')
        self.pack_nuget('src/ohNetGeneratedProviders.Combined.nuspec')


        if not publish_release:
            print('NOT PUBLISHING')
        else:
            self.publish_nuget(os.path.join('build', 'packages', '*.nupkg'), nuget_api_key)

    def pack_nuget(self, project_name, base_path='.', output_path='build/packages'):
        props_str = f'Configuration=Release;version={self.release_version}'

        cmd = ['./nuget/nuget.exe', 'pack', project_name, '-BasePath', base_path, '-Properties', props_str]
        if output_path is not None:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            cmd += ['-OutputDirectory', output_path]

        print(f'Packaging: {project_name}')
        print(f'\n{cmd}')
        subprocess.check_call(cmd)

    def publish_nuget(self, package, api_key=None, server=None, config_file='nuget.config'):
        cmd = ['./nuget/nuget.exe', 'push', package]

        #nuget can be slow, so set a long timeout (in secs)
        cmd += ['-Timeout', '10000']
        cmd += ['-Source', 'https://api.nuget.org/v3/index.json'] 

        print(f'Publishing: {package}')
        print(f'\n{cmd}')
        subprocess.check_call(cmd)
              

if __name__ == '__main__':

    nuget_api_key           = ''
    ohnet_version           = ''
    ohnet_generated_version = ''
    release_version         = '0.0.1'
    publish_release         = 'false'


    try:
        nuget_api_key = os.environ['NUGET_API_KEY']
    except:
        pass

    try:
        ohnet_version           = os.environ['OHNET_VERSION']
        ohnet_generated_version = os.environ['OHNET_GENERATED_VERSION']
    except:
        print('No ohNet version(s) specified')
        sys.exit(1)

    try:
        release_version = os.environ['RELEASE_VERSION']
    except:
        pass

    try:
        publish_release = os.environ['PUBLISH_RELEASE']
    except:
        pass
        
    if not release_version and publish_release:
        print('Publish specified but no release version')
        sys.exit(1)

    if not nuget_api_key and publish_release:
        print('Publish specified but no nuget API key provided')
        sys.exit(1)
    

    print('Running ohNetPackaging...')
    print('-------')
    print(f'    ohNet Version: {ohnet_version}')
    print(f'ohNet Gen Version: {ohnet_generated_version}')
    print(f'  Release Version: {release_version}')
    print(f'  Publish Release: {publish_release}')
    print(f'    Nuget API Key: present')
    print('-------')

    os.chdir('ohNetPackaging')

    b = Runner(nuget_api_key, ohnet_version, ohnet_generated_version, release_version, publish_release)
