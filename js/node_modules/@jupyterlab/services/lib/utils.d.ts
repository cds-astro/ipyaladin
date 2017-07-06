import { JSONObject } from 'phosphor/lib/algorithm/json';
/**
 * Copy the contents of one object to another, recursively.
 *
 * From [stackoverflow](http://stackoverflow.com/a/12317051).
 */
export declare function extend(target: any, source: any): any;
/**
 * Get a deep copy of a JSON object.
 */
export declare function copy(object: JSONObject): JSONObject;
/**
 * Get a random 32 character hex string (not a formal UUID)
 */
export declare function uuid(): string;
/**
 * A URL object.
 *
 * This interface is from the npm package URL object interface. We
 * include it here so that downstream libraries do not have to include
 * the `url` typing files, since the npm `url` package is not in the
 * @types system.
 */
export interface IUrl {
    href?: string;
    protocol?: string;
    auth?: string;
    hostname?: string;
    port?: string;
    host?: string;
    pathname?: string;
    search?: string;
    query?: string | any;
    slashes?: boolean;
    hash?: string;
    path?: string;
}
/**
 * Parse a url into a URL object.
 *
 * @param urlString - The URL string to parse.
 *
 * @param parseQueryString - If `true`, the query property will always be set
 *   to an object returned by the `querystring` module's `parse()` method.
 *   If `false`, the `query` property on the returned URL object will be an
 *   unparsed, undecoded string. Defaults to `false`.
 *
 * @param slashedDenoteHost - If `true`, the first token after the literal
 *   string `//` and preceeding the next `/` will be interpreted as the `host`.
 *   For instance, given `//foo/bar`, the result would be
 *   `{host: 'foo', pathname: '/bar'}` rather than `{pathname: '//foo/bar'}`.
 *   Defaults to `false`.
 *
 * @returns A URL object.
 */
export declare function urlParse(urlStr: string, parseQueryString?: boolean, slashesDenoteHost?: boolean): IUrl;
/**
 * Resolve a url.
 *
 * Take a base URL, and a href URL, and resolve them as a browser would for
 * an anchor tag.
 */
export declare function urlResolve(from: string, to: string): string;
/**
 * Join a sequence of url components and normalizes as in node `path.join`.
 */
export declare function urlPathJoin(...parts: string[]): string;
/**
 * Encode the components of a multi-segment url.
 *
 * #### Notes
 * Preserves the `'/'` separators.
 * Should not include the base url, since all parts are escaped.
 */
export declare function urlEncodeParts(uri: string): string;
/**
 * Return a serialized object string suitable for a query.
 *
 * From [stackoverflow](http://stackoverflow.com/a/30707423).
 */
export declare function jsonToQueryString(json: JSONObject): string;
/**
 * Input settings for an AJAX request.
 */
export interface IAjaxSettings extends JSONObject {
    /**
     * The HTTP method to use.  Defaults to `'GET'`.
     */
    method?: string;
    /**
     * The return data type (used to parse the return data).
     */
    dataType?: string;
    /**
     * The outgoing content type, used to set the `Content-Type` header.
     */
    contentType?: string;
    /**
     * The request data.
     */
    data?: any;
    /**
     * Whether to cache the response. Defaults to `true`.
     */
    cache?: boolean;
    /**
     * The number of milliseconds a request can take before automatically
     * being terminated.  A value of 0 (which is the default) means there is
     * no timeout.
     */
    timeout?: number;
    /**
     * A mapping of request headers, used via `setRequestHeader`.
     */
    requestHeaders?: {
        [key: string]: string;
    };
    /**
     * Is a Boolean that indicates whether or not cross-site Access-Control
     * requests should be made using credentials such as cookies or
     * authorization headers.  Defaults to `false`.
     */
    withCredentials?: boolean;
    /**
     * The user name associated with the request.  Defaults to `''`.
     */
    user?: string;
    /**
     * The password associated with the request.  Defaults to `''`.
     */
    password?: string;
}
/**
 * Data for a successful  AJAX request.
 */
export interface IAjaxSuccess {
    /**
     * The `onload` event.
     */
    readonly event: ProgressEvent;
    /**
     * The XHR object.
     */
    readonly xhr: XMLHttpRequest;
    /**
     * The ajax settings associated with the request.
     */
    readonly ajaxSettings: IAjaxSettings;
    /**
     * The data returned by the ajax call.
     */
    readonly data: any;
}
/**
 * Data for an unsuccesful AJAX request.
 */
export interface IAjaxError {
    /**
     * The event triggering the error.
     */
    readonly event: Event;
    /**
     * The XHR object.
     */
    readonly xhr: XMLHttpRequest;
    /**
     * The ajax settings associated with the request.
     */
    readonly ajaxSettings: IAjaxSettings;
    /**
     * The error message, if `onerror`.
     */
    readonly throwError?: string;
}
/**
 * Asynchronous XMLHTTPRequest handler.
 *
 * @param url - The url to request.
 *
 * @param settings - The settings to apply to the request and response.
 *
 * #### Notes
 * Based on this [example](http://www.html5rocks.com/en/tutorials/es6/promises/#toc-promisifying-xmlhttprequest).
 */
export declare function ajaxRequest(url: string, ajaxSettings: IAjaxSettings): Promise<IAjaxSuccess>;
/**
 * Create an ajax error from an ajax success.
 *
 * @param success - The original success object.
 *
 * @param throwError - The optional new error name.  If not given
 *  we use "Invalid Status: <xhr.status>"
 */
export declare function makeAjaxError(success: IAjaxSuccess, throwError?: string): Promise<any>;
/**
 * Try to load an object from a module or a registry.
 *
 * Try to load an object from a module asynchronously if a module
 * is specified, otherwise tries to load an object from the global
 * registry, if the global registry is provided.
 */
export declare function loadObject(name: string, moduleName: string, registry?: {
    [key: string]: any;
}): Promise<any>;
/**
 * A Promise that can be resolved or rejected by another object.
 */
export declare class PromiseDelegate<T> {
    /**
     * Construct a new Promise delegate.
     */
    constructor();
    /**
     * Get the underlying Promise.
     */
    readonly promise: Promise<T>;
    /**
     * Resolve the underlying Promise with an optional value or another Promise.
     */
    resolve(value?: T | Promise<T>): void;
    /**
     * Reject the underlying Promise with an optional reason.
     */
    reject(reason?: any): void;
    private _promise;
    private _resolve;
    private _reject;
}
/**
 * Get global configuration data for the Jupyter application.
 *
 * @param name - The name of the configuration option.
 *
 * @returns The config value or `undefined` if not found.
 *
 * #### Notes
 * For browser based applications, it is assumed that the page HTML
 * includes a script tag with the id `jupyter-config-data` containing the
 * configuration as valid JSON.
 */
export declare function getConfigOption(name: string): string;
/**
 * Get the base URL for a Jupyter application.
 */
export declare function getBaseUrl(): string;
/**
 * Get the base websocket URL for a Jupyter application.
 */
export declare function getWsUrl(baseUrl?: string): string;
/**
 * Add token to ajaxSettings.requestHeaders if defined.
 * Always returns a copy of ajaxSettings, and a dict.
 */
export declare function ajaxSettingsWithToken(ajaxSettings?: IAjaxSettings, token?: string): IAjaxSettings;
