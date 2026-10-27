/* eslint-disable */

// @ts-nocheck

import { Route as rootRouteImport } from './routes/__root'
import { Route as SettingsRouteImport } from './routes/settings'
import { Route as SearchRouteImport } from './routes/search'
import { Route as ResultsRouteImport } from './routes/results'
import { Route as PermissionRouteImport } from './routes/permission'
import { Route as GuidanceRouteImport } from './routes/guidance'
import { Route as IndexRouteImport } from './routes/index'
import { Route as ResultsRouteIdRouteImport } from './routes/results.$routeId'

const SettingsRoute = SettingsRouteImport.update({
  id: '/settings',
  path: '/settings',
  getParentRoute: () => rootRouteImport,
} as any)
const SearchRoute = SearchRouteImport.update({
  id: '/search',
  path: '/search',
  getParentRoute: () => rootRouteImport,
} as any)
const ResultsRoute = ResultsRouteImport.update({
  id: '/results',
  path: '/results',
  getParentRoute: () => rootRouteImport,
} as any)
const PermissionRoute = PermissionRouteImport.update({
  id: '/permission',
  path: '/permission',
  getParentRoute: () => rootRouteImport,
} as any)
const GuidanceRoute = GuidanceRouteImport.update({
  id: '/guidance',
  path: '/guidance',
  getParentRoute: () => rootRouteImport,
} as any)
const IndexRoute = IndexRouteImport.update({
  id: '/',
  path: '/',
  getParentRoute: () => rootRouteImport,
} as any)
const ResultsRouteIdRoute = ResultsRouteIdRouteImport.update({
  id: '/$routeId',
  path: '/$routeId',
  getParentRoute: () => ResultsRoute,
} as any)

export interface FileRoutesByFullPath {
  '/': typeof IndexRoute
  '/guidance': typeof GuidanceRoute
  '/permission': typeof PermissionRoute
  '/results': typeof ResultsRouteWithChildren
  '/search': typeof SearchRoute
  '/settings': typeof SettingsRoute
  '/results/$routeId': typeof ResultsRouteIdRoute
}
export interface FileRoutesByTo {
  '/': typeof IndexRoute
  '/guidance': typeof GuidanceRoute
  '/permission': typeof PermissionRoute
  '/results': typeof ResultsRouteWithChildren
  '/search': typeof SearchRoute
  '/settings': typeof SettingsRoute
  '/results/$routeId': typeof ResultsRouteIdRoute
}
export interface FileRoutesById {
  __root__: typeof rootRouteImport
  '/': typeof IndexRoute
  '/guidance': typeof GuidanceRoute
  '/permission': typeof PermissionRoute
  '/results': typeof ResultsRouteWithChildren
  '/search': typeof SearchRoute
  '/settings': typeof SettingsRoute
  '/results/$routeId': typeof ResultsRouteIdRoute
}
export interface FileRouteTypes {
  fileRoutesByFullPath: FileRoutesByFullPath
  fullPaths:
    | '/'
    | '/guidance'
    | '/permission'
    | '/results'
    | '/search'
    | '/settings'
    | '/results/$routeId'
  fileRoutesByTo: FileRoutesByTo
  to:
    | '/'
    | '/guidance'
    | '/permission'
    | '/results'
    | '/search'
    | '/settings'
    | '/results/$routeId'
  id:
    | '__root__'
    | '/'
    | '/guidance'
    | '/permission'
    | '/results'
    | '/search'
    | '/settings'
    | '/results/$routeId'
  fileRoutesById: FileRoutesById
}
export interface RootRouteChildren {
  IndexRoute: typeof IndexRoute
  GuidanceRoute: typeof GuidanceRoute
  PermissionRoute: typeof PermissionRoute
  ResultsRoute: typeof ResultsRouteWithChildren
  SearchRoute: typeof SearchRoute
  SettingsRoute: typeof SettingsRoute
}

declare module '@tanstack/react-router' {
  interface FileRoutesByPath {
    '/': {
      id: '/'
      path: '/'
      fullPath: '/'
      preLoaderRoute: typeof IndexRouteImport
      parentRoute: typeof rootRouteImport
    }
    '/guidance': {
      id: '/guidance'
      path: '/guidance'
      fullPath: '/guidance'
      preLoaderRoute: typeof GuidanceRouteImport
      parentRoute: typeof rootRouteImport
    }
    '/permission': {
      id: '/permission'
      path: '/permission'
      fullPath: '/permission'
      preLoaderRoute: typeof PermissionRouteImport
      parentRoute: typeof rootRouteImport
    }
    '/results': {
      id: '/results'
      path: '/results'
      fullPath: '/results'
      preLoaderRoute: typeof ResultsRouteImport
      parentRoute: typeof rootRouteImport
    }
    '/search': {
      id: '/search'
      path: '/search'
      fullPath: '/search'
      preLoaderRoute: typeof SearchRouteImport
      parentRoute: typeof rootRouteImport
    }
    '/settings': {
      id: '/settings'
      path: '/settings'
      fullPath: '/settings'
      preLoaderRoute: typeof SettingsRouteImport
      parentRoute: typeof rootRouteImport
    }
    '/results/$routeId': {
      id: '/results/$routeId'
      path: '/$routeId'
      fullPath: '/results/$routeId'
      preLoaderRoute: typeof ResultsRouteIdRouteImport
      parentRoute: typeof ResultsRoute
    }
  }
}

interface ResultsRouteChildren {
  ResultsRouteIdRoute: typeof ResultsRouteIdRoute
}

const ResultsRouteChildren: ResultsRouteChildren = {
  ResultsRouteIdRoute: ResultsRouteIdRoute,
}

const ResultsRouteWithChildren = ResultsRoute._addFileChildren(ResultsRouteChildren)

const rootRouteChildren: RootRouteChildren = {
  IndexRoute: IndexRoute,
  GuidanceRoute: GuidanceRoute,
  PermissionRoute: PermissionRoute,
  ResultsRoute: ResultsRouteWithChildren,
  SearchRoute: SearchRoute,
  SettingsRoute: SettingsRoute,
}
export const routeTree = rootRouteImport
  ._addFileChildren(rootRouteChildren)
  ._addFileTypes<FileRouteTypes>()

import type { getRouter } from './router.tsx'
import type { startInstance } from './start.ts'
declare module '@tanstack/react-start' {
  interface Register {
    ssr: true
    router: Awaited<ReturnType<typeof getRouter>>
    config: Awaited<ReturnType<typeof startInstance.getOptions>>
  }
}
