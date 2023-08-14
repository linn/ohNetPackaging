# Defines the build behaviour for continuous integration builds.

import sys
import os
import shutil
import glob
import subprocess

try:
    from ci import (OpenHomeBuilder, require_version)
except ImportError:
    print "You need to update ohDevTools."
    sys.exit(1)

require_version(67)



class Builder(OpenHomeBuilder):
    output_dir = "build/packages"
    build_dir = "build"

    def pack_nuget(self, project_name, base_path='', props=None, output_path='build/packages', include_references=True):
        '''
        Creates a nuget package based on the supplied project file
        '''
        props = {} if props is None else props
        props['Configuration'] = self.configuration
        props['version'] = self.version if self.version is not None else '0.0.0.1-dev'
        props_str = ';'.join(['%s=%s' % (k, v) for (k, v) in props.items()])

        args = ['./nuget/nuget.exe', 'pack', project_name, '-BasePath', base_path, '-Properties', props_str]
        if output_path is not None:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            args += ['-OutputDirectory', output_path]
        if include_references:
            args += ['-IncludeReferencedProjects']
        self.cli(args)

    def publish_nuget(self, package, api_key=None, server=None, config_file='nuget.config'):
        '''
        Publishes a nuget package to a specified NuGet server.
        '''
        args = ['./nuget/nuget.exe', 'push', package]

        #nuget can be slow, so set a long timeout (in secs)
        args += ['-Timeout', "10000"]

        if api_key is not None:
            args += [api_key]
        if server is not None:
            args += ['-Source', server]
        if config_file is not None and os.path.isfile(config_file):
            args += ['-ConfigFile', config_file]
        self.cli(args)

    def setup(self):
        self.nuget_api_key = self.env.get('NUGET_API_KEY')
		
        # write release version in dependencies.json
        f1 = open('projectdata/dependencies.json', 'r')
        c = f1.read() % {'ohnet_version' : self.env.get('OHNET_VERSION'), 'ohnet_generated_version' : self.env.get('OHNET_GENERATED_VERSION')}
        f1.close()
		
        f2 = open('projectdata/dependencies.json', 'w')
        f2.write(c)
        f2.close()

    def clean(self):
        if os.path.isdir(self.build_dir):
            shutil.rmtree(self.build_dir)

    def build(self):
        self.pack_nuget('src/ohNet.nuspec', '.')
        self.pack_nuget('src/ohNet.NET.nuspec', '.')
        # NOTE: The multi-DLL packages are no longer build and published as we don't consume them. Can be re-enabled if this suddenly becomes a requirement
        print('NOTE: multi-DLL packages for proxies & providers are no longer built.')
        #self.pack_nuget('src/ohNetGeneratedProxies.nuspec', '.')
        #self.pack_nuget('src/ohNetGeneratedProviders.nuspec', '.')
        self.pack_nuget('src/ohNetGeneratedProxies.Combined.nuspec', '.')
        self.pack_nuget('src/ohNetGeneratedProviders.Combined.nuspec', '.')

    def publish(self):
        self.publish_nuget(os.path.join('build', 'packages', '*.nupkg'), self.nuget_api_key, 'https://api.nuget.org/v3/index.json')
